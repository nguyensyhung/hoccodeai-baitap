## Prompt 1

```
Bạn là một giáo viên có kinh nghiệm tạo câu hỏi trắc nghiệm.

Hãy đọc kỹ nội dung bài học dưới đây và thực hiện các bước sau:
1. Xác định các khái niệm chính và kiến thức quan trọng trong bài học
2. Tạo câu hỏi trắc nghiệm cho mỗi khái niệm (mỗi câu có 4 đáp án A, B, C, D)
3. Chỉ rõ đáp án đúng cho mỗi câu

Tạo ít nhất 3 câu hỏi trắc nghiệm.

Format đầu ra theo JSON:
{
  "questions": [
    {
      "question": "Nội dung câu hỏi",
      "options": {
        "A": "Đáp án A",
        "B": "Đáp án B",
        "C": "Đáp án C",
        "D": "Đáp án D"
      },
      "correct_answer": "A",
      "explanation": "Giải thích tại sao đáp án này đúng"
    }
  ]
}

Nội dung bài học:
"""
[Nội dung bài học]
"""
```

---

## Prompt 2

```
Bạn là một nhà văn chuyên nghiệp.

Đọc đoạn văn dưới đây và thực hiện phân tích theo các bước:
1. Xác định chủ đề chính của đoạn văn
2. Phân tích phong cách viết (trang trọng, thân mật, học thuật, sáng tạo...)
3. Viết thêm 2-3 đoạn văn tiếp theo phù hợp với phong cách và chủ đề

Đoạn văn gốc:
"""
[Đoạn văn]
"""

Format đầu ra:
## Phân tích
- Chủ đề: [chủ đề chính]
- Phong cách: [mô tả phong cách]

## Đoạn văn tiếp theo
[Nội dung viết thêm 2-3 đoạn]
```

---

## Prompt 3

```
Bạn là một chuyên gia phân tích dữ liệu khách hàng.

Nhiệm vụ của bạn:
1. Đọc kỹ từng review trong danh sách
2. Phân loại mỗi review thành "tích cực" hoặc "tiêu cực" dựa trên nội dung
3. Đếm tổng số review tích cực và tiêu cực

Ví dụ phân loại:
- "Sản phẩm tuyệt vời, giao hàng nhanh!" → Tích cực
- "Chất lượng kém, không đáng tiền" → Tiêu cực
- "Tạm ổn, không có gì đặc biệt" → Tiêu cực

Danh sách review:
"""
[Danh sách review]
"""

Trả về kết quả dưới dạng JSON:
{
  "summary": {
    "positive_count": 0,
    "negative_count": 0
  }
}
```

---

## Prompt 4

```
Bạn là một senior developer có kinh nghiệm code review và debug.

Hãy phân tích đoạn code dưới đây theo các bước sau:
1. Đọc và hiểu logic của code
2. Tìm các bug, lỗi logic, hoặc vấn đề về performance
3. Giải thích rõ ràng code đang làm gì (theo từng phần)
4. Thêm comment chi tiết vào code

Đoạn code:
```
[Code cần giải thích]
```

Format đầu ra:
## 1. Tổng quan
[Mô tả ngắn gọn code đang làm gì]

## 2. Các bug tìm thấy
- Bug 1: [Mô tả bug và vị trí]
- Bug 2: [Mô tả bug và vị trí]

## 3. Code với comment
```
[Code đã được thêm comment chi tiết]
```

## 4. Code đã sửa lỗi
```
[Code sau khi sửa bug]

---

## Prompt 5

```
Bạn là một hướng dẫn viên du lịch chuyên nghiệp với kiến thức sâu rộng về các địa điểm du lịch.

Hãy cung cấp thông tin chi tiết về địa điểm du lịch theo các bước:
1. Giới thiệu tổng quan về địa điểm
2. Liệt kê các điểm tham quan nổi bật (ít nhất 5 điểm)
3. Giới thiệu món ăn đặc sản địa phương (ít nhất 5 món)
4. Đề xuất thời gian lý tưởng để tham quan

Địa điểm: [Tên địa điểm]

Format đầu ra dưới dạng JSON:
{
  "destination": "Tên địa điểm",
  "overview": "Giới thiệu tổng quan",
  "top_attractions": [
    {
      "name": "Tên điểm tham quan",
      "description": "Mô tả",
      "suggested_duration": "Thời gian tham quan"
    }
  ],
  "local_food": [
    {
      "name": "Tên món ăn",
      "description": "Mô tả món ăn",
      "where_to_try": "Địa điểm nên thử"
    }
  ],
  "best_time_to_visit": "Thời gian lý tưởng",
}
```

---

## Prompt 6

```
Bạn là một nhà phê bình văn học với khả năng phân tích và tóm tắt nội dung sách xuất sắc.

Hãy đọc kỹ nội dung cuốn sách/chương sách và thực hiện theo các bước:
1. Tóm tắt nội dung chính theo cấu trúc: Mở đầu → Phát triển → Cao trào → Kết thúc
2. Liệt kê tất cả nhân vật xuất hiện

Nội dung sách:
"""
[Nội dung sách]
"""

Format đầu ra dưới dạng JSON:
{
  "book_info": {
    "title": "Tên sách (nếu có)",
    "genre": "Thể loại",
    "setting": "Bối cảnh thời gian và địa điểm"
  },
  "summary": {
    "opening": "Mở đầu câu chuyện",
    "development": "Phát triển sự kiện",
    "climax": "Cao trào",
    "resolution": "Kết thúc"
  },
  "characters": [
    {
      "name": "Tên nhân vật",
      "role": "Vai trò (nhân vật chính/phụ)",
      "description": "Mô tả đặc điểm",
      "relationships": ["Quan hệ với nhân vật khác"]
    }
  ]
}
```