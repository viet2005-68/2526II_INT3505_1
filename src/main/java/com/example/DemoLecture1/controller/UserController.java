package com.example.DemoLecture1.controller;

import com.example.DemoLecture1.dto.UserRequest;
import com.example.DemoLecture1.dto.UserResponse;
import com.example.DemoLecture1.service.UserService;
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
     * HTTP Status: 201 Created | 409 Conflict (email đã tồn tại)
     */
    @PostMapping
    public ResponseEntity<UserResponse> createUser(@RequestBody UserRequest request) {
        UserResponse createdUser = userService.createUser(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdUser);
    }
    
    /**
     * PUT /api/users/{id} - Cập nhật toàn bộ thông tin người dùng
     * HTTP Status: 200 OK | 404 Not Found | 409 Conflict
     */
    @PutMapping("/{id}")
    public ResponseEntity<UserResponse> updateUser(
            @PathVariable Long id,
            @RequestBody UserRequest request) {
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
}
