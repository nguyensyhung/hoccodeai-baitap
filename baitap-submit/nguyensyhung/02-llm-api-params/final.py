```python
def fibonacci_sequence(n):
    # Khởi tạo dãy Fibonacci
    fib_sequence = []
    
    # Các số đầu tiên của dãy Fibonacci
    a, b = 0, 1
    
    # Lặp để tạo n số đầu tiên trong dãy Fibonacci
    for _ in range(n):
        fib_sequence.append(a)  # Thêm số a vào dãy
        a, b = b, a + b  # Cập nhật a và b

    return fib_sequence

# Xử lý input từ người dùng
try:
    n = int(input("Nhập số lượng số Fibonacci bạn muốn in ra: "))
    if n < 0:
        print("Vui lòng nhập một số nguyên không âm.")
    else:
        # Gọi hàm và in kết quả
        result = fibonacci_sequence(n)
        print("Dãy Fibonacci đầu tiên gồm", n, "số là:", result)
except ValueError:
    print("Vui lòng nhập một số nguyên hợp lệ.")
```