package com.example.DemoLecture1.controller;

import com.example.DemoLecture1.dto.UserRequest;
import com.example.DemoLecture1.dto.UserResponse;
import com.example.DemoLecture1.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {
    
    private final UserService userService;
    
    /**
     * GET /api/users - Lấy danh sách tất cả người dùng
     * HTTP Status: 200 OK
     */
    @GetMapping
    public ResponseEntity<List<UserResponse>> getAllUsers() {
        List<UserResponse> users = userService.getAllUsers();
        return ResponseEntity.ok(users);
    }
    
    /**
     * GET /api/users/{id} - Lấy thông tin người dùng theo ID
     * HTTP Status: 200 OK | 404 Not Found
     */
    @GetMapping("/{id}")
    public ResponseEntity<UserResponse> getUserById(@PathVariable Long id) {
        UserResponse user = userService.getUserById(id);
        return ResponseEntity.ok(user);
    }
    
    /**
     * GET /api/users/email/{email} - Tìm người dùng theo email
     * HTTP Status: 200 OK | 404 Not Found
     */
    @GetMapping("/email/{email}")
    public ResponseEntity<UserResponse> getUserByEmail(@PathVariable String email) {
        UserResponse user = userService.getUserByEmail(email);
        return ResponseEntity.ok(user);
    }
    
    /**
     * POST /api/users - Tạo người dùng mới
     * HTTP Status: 201 Created | 400 Bad Request | 409 Conflict (email đã tồn tại)
     */
    @PostMapping
    public ResponseEntity<UserResponse> createUser(@Valid @RequestBody UserRequest request) {
        UserResponse createdUser = userService.createUser(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdUser);
    }
    
    /**
     * PUT /api/users/{id} - Cập nhật toàn bộ thông tin người dùng
     * HTTP Status: 200 OK | 400 Bad Request | 404 Not Found | 409 Conflict
     */
    @PutMapping("/{id}")
    public ResponseEntity<UserResponse> updateUser(
            @PathVariable Long id,
            @Valid @RequestBody UserRequest request) {
        UserResponse updatedUser = userService.updateUser(id, request);
        return ResponseEntity.ok(updatedUser);
    }
    
    /**
     * PATCH /api/users/{id} - Cập nhật một phần thông tin người dùng
     * HTTP Status: 200 OK | 404 Not Found | 409 Conflict
     */
    @PatchMapping("/{id}")
    public ResponseEntity<UserResponse> patchUser(
            @PathVariable Long id,
            @RequestBody UserRequest request) {
        UserResponse updatedUser = userService.patchUser(id, request);
        return ResponseEntity.ok(updatedUser);
    }
    
    /**
     * DELETE /api/users/{id} - Xóa người dùng
     * HTTP Status: 204 No Content | 404 Not Found
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userService.deleteUser(id);
        return ResponseEntity.noContent().build();
    }
    
    // ==========================================
    // TEST ENDPOINTS - Demo 500 Error
    // ==========================================
    
    /**
     * TEST: NullPointerException - 500 Error
     * Demo lỗi khi code cố gọi method trên null object
     */
    @GetMapping("/test-500-npe")
    public ResponseEntity<String> testNullPointerException() {
        String str = null;
        // Cố gọi method trên null → NullPointerException
        return ResponseEntity.ok(str.toUpperCase());
    }
    
    /**
     * TEST: ArithmeticException - 500 Error
     * Demo lỗi chia cho 0
     */
    @GetMapping("/test-500-divide-zero")
    public ResponseEntity<Integer> testDivideByZero() {
        int result = 10 / 0;  // ArithmeticException: / by zero
        return ResponseEntity.ok(result);
    }
    
    /**
     * TEST: IndexOutOfBoundsException - 500 Error
     * Demo lỗi truy cập index không tồn tại
     */
    @GetMapping("/test-500-array")
    public ResponseEntity<String> testArrayIndexOutOfBounds() {
        String[] array = new String[0];
        // Array empty nhưng cố lấy phần tử đầu tiên
        return ResponseEntity.ok(array[0]);
    }
    
    /**
     * TEST: StackOverflowError - 500 Error
     * Demo lỗi đệ quy vô hạn
     */
    @GetMapping("/test-500-stackoverflow")
    public ResponseEntity<String> testStackOverflow() {
        // Gọi chính nó → infinite recursion
        return testStackOverflow();
    }
    
    /**
     * TEST: ClassCastException - 500 Error
     * Demo lỗi ép kiểu sai
     */
    @GetMapping("/test-500-classcast")
    public ResponseEntity<String> testClassCastException() {
        Object obj = Integer.valueOf(123);
        // Cố ép Integer thành String → ClassCastException
        String str = (String) obj;
        return ResponseEntity.ok(str);
    }
}
