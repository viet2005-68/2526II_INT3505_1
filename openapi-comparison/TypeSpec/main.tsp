import "@typespec/http";
import "@typespec/openapi3";

using Http;

@service(#{
  title: "Library API",
})
@server("http://localhost:4001", "Local development server")
namespace LibraryAPI;

// ─── Models ───────────────────────────────────────────────

model Book {
  @visibility(Lifecycle.Read)
  id: int32;

  title: string;
  author: string;
  year: int32;
}

model ErrorResponse {
  error: string;
}

// ─── Books endpoints ──────────────────────────────────────

@route("/books")
interface Books {
  /** Get all books */
  @get
  list(): Book[];

  /** Get book by ID */
  @get
  @route("/{id}")
  get(
    @path id: int32,
  ): Book | {
    @statusCode statusCode: 404;
    @body body: ErrorResponse;
  };
}
