import http from "k6/http";
import { check, sleep, group } from "k6";
import { Trend } from "k6/metrics";

export let options = {
  vus: 20,
  duration: "30s",
  thresholds: {
    http_req_duration: ["p(95)<500"],
    http_req_failed: ["rate<0.01"],
  },
  summaryTrendStats: ["avg", "min", "med", "max", "p(90)", "p(95)", "p(99)"],
};

const BASE_URL = "http://127.0.0.1:8003";

// Custom metrics để đo response time cho từng nhóm endpoint
let booksTrend = new Trend("books_duration");
let bookCursorTrend = new Trend("books_cursor_duration");
let bookDetailTrend = new Trend("book_detail_duration");
let bookCreateTrend = new Trend("book_create_duration");
let bookUpdateTrend = new Trend("book_update_duration");
let bookDeleteTrend = new Trend("book_delete_duration");
let usersTrend = new Trend("users_duration");
let userDetailTrend = new Trend("user_detail_duration");
let userCreateTrend = new Trend("user_create_duration");
let loansTrend = new Trend("loans_duration");
let loanCreateTrend = new Trend("loan_create_duration");
let loanReturnTrend = new Trend("loan_return_duration");

// Dữ liệu ngẫu nhiên để tạo user / book mỗi iteration
const randomSuffix = () => `${__VU}_${__ITER}_${Date.now()}`;

export default function () {
  let createdUserId = null;
  let createdBookId = null;
  let createdLoanId = null;
  let createdAuthorName = `Author_${randomSuffix()}`;

  // ── USERS ──────────────────────────────────────────────────────────────────

  group("Users - List", function () {
    let res = http.get(`${BASE_URL}/users/?page=1&per_page=10`);
    usersTrend.add(res.timings.duration);

    if (
      !check(res, {
        "Users list 200": (r) => r.status === 200,
        "Users data exists": (r) => r.json("data") !== null,
        "Users metadata success": (r) => r.json("metadata.success") === true,
      })
    ) {
      console.error(`Users list error: ${res.status} - ${res.body}`);
    }
  });

  group("Users - Create", function () {
    let suffix = randomSuffix();
    let payload = JSON.stringify({
      username: `user_${suffix}`,
      email: `user_${suffix}@test.com`,
      password: "password123",
    });

    let res = http.post(`${BASE_URL}/users/`, payload, {
      headers: { "Content-Type": "application/json" },
    });
    userCreateTrend.add(res.timings.duration);

    if (
      !check(res, {
        "User created 201": (r) => r.status === 201,
        "User id returned": (r) => r.json("data.id") !== undefined,
        "Create success metadata": (r) => r.json("metadata.success") === true,
      })
    ) {
      console.error(`User create error: ${res.status} - ${res.body}`);
      return;
    }

    createdUserId = res.json("data.id");
  });

  if (createdUserId !== null) {
    group("Users - Get Detail", function () {
      let res = http.get(`${BASE_URL}/users/${createdUserId}`);
      userDetailTrend.add(res.timings.duration);

      if (
        !check(res, {
          "User detail 200": (r) => r.status === 200,
          "User detail has id": (r) => r.json("data.id") === createdUserId,
        })
      ) {
        console.error(`User detail error: ${res.status} - ${res.body}`);
      }
    });

    group("Users - Create with missing fields (expect 400)", function () {
      let res = http.post(
        `${BASE_URL}/users/`,
        JSON.stringify({ username: "incomplete_user" }),
        { headers: { "Content-Type": "application/json" } }
      );

      if (
        !check(res, {
          "Missing fields returns 400": (r) => r.status === 400,
          "Error reported": (r) => r.json("error") !== null,
        })
      ) {
        console.error(`Missing fields check error: ${res.status} - ${res.body}`);
      }
    });
  }

  // ── BOOKS ──────────────────────────────────────────────────────────────────

  group("Books - List (pagination)", function () {
    let res = http.get(`${BASE_URL}/books/?page=1&per_page=10`);
    booksTrend.add(res.timings.duration);

    if (
      !check(res, {
        "Books list 200": (r) => r.status === 200,
        "Books data is array": (r) => Array.isArray(r.json("data")),
        "Books metadata success": (r) => r.json("metadata.success") === true,
      })
    ) {
      console.error(`Books list error: ${res.status} - ${res.body}`);
    }
  });

  group("Books - Cursor pagination", function () {
    let res = http.get(`${BASE_URL}/books/cursor?limit=10`);
    bookCursorTrend.add(res.timings.duration);

    if (
      !check(res, {
        "Books cursor 200": (r) => r.status === 200,
        "Cursor pagination type": (r) =>
          r.json("metadata.pagination.type") === "cursor",
        "Has has_more field": (r) =>
          r.json("metadata.pagination.has_more") !== undefined,
      })
    ) {
      console.error(`Books cursor error: ${res.status} - ${res.body}`);
    }
  });

  group("Books - Search by title", function () {
    let res = http.get(`${BASE_URL}/books/?search=the&page=1&per_page=5`);
    booksTrend.add(res.timings.duration);

    if (
      !check(res, {
        "Books search 200": (r) => r.status === 200,
        "Books search data exists": (r) => r.json("data") !== null,
      })
    ) {
      console.error(`Books search error: ${res.status} - ${res.body}`);
    }
  });

  group("Books - Create", function () {
    let suffix = randomSuffix();
    let payload = JSON.stringify({
      title: `Book_${suffix}`,
      price: Math.floor(Math.random() * 100) + 10,
      author_name: createdAuthorName,
      quantity: 5,
    });

    let res = http.post(`${BASE_URL}/books/`, payload, {
      headers: { "Content-Type": "application/json" },
    });
    bookCreateTrend.add(res.timings.duration);

    if (
      !check(res, {
        "Book created 201": (r) => r.status === 201,
        "Book id returned": (r) => r.json("data.id") !== undefined,
      })
    ) {
      console.error(`Book create error: ${res.status} - ${res.body}`);
      return;
    }

    createdBookId = res.json("data.id");
  });

  group("Books - Create with missing fields (expect 400)", function () {
    let res = http.post(
      `${BASE_URL}/books/`,
      JSON.stringify({ price: 50 }),
      { headers: { "Content-Type": "application/json" } }
    );

    if (
      !check(res, {
        "Missing title returns 400": (r) => r.status === 400,
        "Error reported": (r) => r.json("error") !== null,
      })
    ) {
      console.error(`Book missing fields check: ${res.status} - ${res.body}`);
    }
  });

  if (createdBookId !== null) {
    group("Books - Get Detail", function () {
      let res = http.get(`${BASE_URL}/books/${createdBookId}`);
      bookDetailTrend.add(res.timings.duration);

      if (
        !check(res, {
          "Book detail 200": (r) => r.status === 200,
          "Book detail has id": (r) => r.json("data.id") === createdBookId,
          "Book detail has author": (r) => r.json("data.author") !== undefined,
        })
      ) {
        console.error(`Book detail error: ${res.status} - ${res.body}`);
      }
    });

    group("Books - Update", function () {
      let res = http.put(
        `${BASE_URL}/books/${createdBookId}`,
        JSON.stringify({ price: 99, quantity: 10 }),
        { headers: { "Content-Type": "application/json" } }
      );
      bookUpdateTrend.add(res.timings.duration);

      if (
        !check(res, {
          "Book updated 200": (r) => r.status === 200,
          "Update success metadata": (r) => r.json("metadata.success") === true,
        })
      ) {
        console.error(`Book update error: ${res.status} - ${res.body}`);
      }
    });
  }

  // ── LOANS ──────────────────────────────────────────────────────────────────

  if (createdUserId !== null && createdBookId !== null) {
    group("Loans - Create", function () {
      let res = http.post(
        `${BASE_URL}/users/${createdUserId}/loans`,
        JSON.stringify({ book_id: createdBookId }),
        { headers: { "Content-Type": "application/json" } }
      );
      loanCreateTrend.add(res.timings.duration);

      if (
        !check(res, {
          "Loan created 201": (r) => r.status === 201,
          "Loan has status active": (r) => r.json("data.status") === "active",
          "Loan has book info": (r) => r.json("data.book") !== undefined,
        })
      ) {
        console.error(`Loan create error: ${res.status} - ${res.body}`);
        return;
      }

      createdLoanId = res.json("data.id");
    });

    group("Loans - List for user", function () {
      let res = http.get(`${BASE_URL}/users/${createdUserId}/loans`);
      loansTrend.add(res.timings.duration);

      if (
        !check(res, {
          "Loans list 200": (r) => r.status === 200,
          "Loans data is array": (r) => Array.isArray(r.json("data")),
        })
      ) {
        console.error(`Loans list error: ${res.status} - ${res.body}`);
      }
    });

    group("Loans - Create duplicate (expect 400)", function () {
      let res = http.post(
        `${BASE_URL}/users/${createdUserId}/loans`,
        JSON.stringify({ book_id: createdBookId }),
        { headers: { "Content-Type": "application/json" } }
      );

      if (
        !check(res, {
          "Duplicate loan returns 400": (r) => r.status === 400,
          "Error reported for duplicate": (r) => r.json("error") !== null,
        })
      ) {
        console.error(`Duplicate loan check: ${res.status} - ${res.body}`);
      }
    });

    if (createdLoanId !== null) {
      group("Loans - Return book", function () {
        let res = http.post(
          `${BASE_URL}/users/${createdUserId}/loans/${createdLoanId}/return`,
          JSON.stringify({}),
          { headers: { "Content-Type": "application/json" } }
        );
        loanReturnTrend.add(res.timings.duration);

        if (
          !check(res, {
            "Return 200": (r) => r.status === 200,
            "Status returned": (r) => r.json("data.status") === "returned",
            "Return date set": (r) => r.json("data.return_date") !== null,
          })
        ) {
          console.error(`Loan return error: ${res.status} - ${res.body}`);
        }
      });

      group("Loans - Return already returned (expect 400)", function () {
        let res = http.post(
          `${BASE_URL}/users/${createdUserId}/loans/${createdLoanId}/return`,
          JSON.stringify({}),
          { headers: { "Content-Type": "application/json" } }
        );

        if (
          !check(res, {
            "Double return 400": (r) => r.status === 400,
            "Error for already returned": (r) => r.json("error") !== null,
          })
        ) {
          console.error(`Double return check: ${res.status} - ${res.body}`);
        }
      });
    }
  }

  // ── CLEANUP: xoá book đã tạo ────────────────────────────────────────────────

  if (createdBookId !== null) {
    group("Books - Delete", function () {
      let res = http.del(`${BASE_URL}/books/${createdBookId}`);
      bookDeleteTrend.add(res.timings.duration);

      if (
        !check(res, {
          "Book deleted 204": (r) => r.status === 204,
        })
      ) {
        console.error(`Book delete error: ${res.status} - ${res.body}`);
      }
    });
  }

  sleep(1);
}
