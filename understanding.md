# Nội dung 10 slide — storyline "Payment Strategy: Từ Subsidy Ngẫu Nhiên Đến Phân Bổ Có Chủ Đích"

*Mạch truyện chung:* Đặt vấn đề (đang bù lỗ mà không rõ hiệu quả) → lật lại giả định sai (methodology trap) → tìm ra 2 đòn bẩy thật (CI tăng trưởng sạch, seller/platform discount độc lập) → định lượng cơ hội → đề xuất chiến lược 2 mũi nhọn → cách triển khai & rủi ro.

---

### Slide 1 — Title / Vấn đề đặt ra
*Thông điệp chính:* Nền tảng đang chi ~$5,519 discount nhưng chỉ thu lại $2,163 phí — câu hỏi là chi đúng chỗ chưa?
*Nội dung:* Bối cảnh case, 500 users/9,935 đơn/6 tháng, con số bù lỗ ròng -$3,356 làm "hook" mở đầu.
*Chart:* Big number callout / waterfall nhỏ: GMV → Discount → Fee → Net position (1 waterfall chart đơn giản 4 cột).

### Slide 2 — Bức tranh hiện trạng: 5 phương thức, 5 vai trò rất khác nhau
*Thông điệp chính:* Không phải phương thức nào cũng "ngang hàng" — mỗi cái đang chơi một cuộc chơi kinh tế khác nhau.
*Nội dung:* Bảng % đơn, AOV, discount/đơn, fee/đơn, net vị thế/đơn cho 5 phương thức.
*Chart:* Bar chart "Net vị thế/đơn theo payment method" (chart đã dùng ở phần trước) + bảng nhỏ AOV bên cạnh.

### Slide 3 — Lật lại giả định: "BNPL/Wallet users là khách kém giá trị"?
*Thông điệp chính:* Không — đó là bẫy phương pháp luận từ ngưỡng ≥50%, thực tế Wallet gắn liền khách trung thành nhất.
*Nội dung:* So sánh segment theo ngưỡng cứng (sai) vs theo bucket tần suất mua (đúng) — Wallet share tăng dần theo mức độ trung thành (19%→31%), NMV tăng theo (13.6→314.7).
*Chart:* Line/bar kết hợp: trục X = order bucket (1/2-3/4-10/11-30/30+), 2 series (Wallet share %, BNPL share %) + đường NMV trung bình trên trục phụ.

### Slide 4 — Credit Installment: "đứa con nuôi" đang âm thầm tăng trưởng sạch
*Thông điệp chính:* CI có discount thấp nhất nhưng AOV cao gấp 5-8 lần — động lực đến từ chính sản phẩm/nhu cầu, không phải khuyến mãi.
*Nội dung:* Discount% (9%) vs AOV (41.56) so với 4 phương thức còn lại; đây là phương thức DUY NHẤT có net dương (+$961).
*Chart:* Scatter/bubble chart: trục X = discount% trung bình, trục Y = AOV, size bubble = số đơn — CI nổi bật ở góc "thấp discount – cao AOV".

### Slide 5 — Nhưng tăng trưởng CI nên đặt cược vào đâu: Beauty hay Fashion?
*Thông điệp chính:* Fashion là bằng chứng "đơn lớn" rõ ràng nhất; Beauty là nguồn volume nhưng cần bóc tách thêm.
*Nội dung:* Beauty: n=265, mean 39.3 nhưng median chỉ 6.06 (lệch phải mạnh); Fashion: n=17, mean/median gần nhau (83.6/97.2) — nêu rõ giới hạn mẫu Fashion.
*Chart:* Box plot GMV theo category cho riêng CI (Beauty vs Fashion vs Home Living) — cho thấy trực quan độ lệch phân phối.

### Slide 6 — Seller discount và Platform discount: hai thế giới song song
*Thông điệp chính:* Hai bên vận hành hoàn toàn độc lập (correlation ≈ 0), kể cả trong ngày sale lớn.
*Nội dung:* Correlation ~0.03 mọi lát cắt; ngày sale (ngày đôi/15/25): seller discount gần như không đổi (3.26%→3.8%) nhưng platform discount tăng vọt (10.69%→16.28%).
*Chart:* Grouped bar chart "Ngày thường vs Ngày sale" × Seller discount% vs Platform discount% (chart đã dùng ở phần trước).

### Slide 7 — Cơ hội tái phân bổ: định lượng được, nhưng có rào chắn
*Thông điệp chính:* ~$1,239 platform discount đang "chồng" lên các đơn seller đã trợ giá cao — có thể tái phân bổ, nhưng phải tránh nhóm nhạy giá.
*Nội dung:* Top-quartile seller-discount (2,484 đơn) vẫn nhận platform discount 14.02% (cao hơn TB); overlap với discount-sensitive user 82.6% (rủi ro) vs high-value user chỉ 27.9% (an toàn).
*Chart:* Dashboard 2 phần: (1) bar "$ discount pool theo seller-discount bucket", (2) stacked bar overlap % với discount-sensitive/high-value segment.

### Slide 8 — Chiến lược 2 mũi nhọn: Growth sạch (CI) + Cross-subsidy có kiểm soát (BNPL/Wallet)
*Thông điệp chính:* Một bên nuôi tăng trưởng không cần đốt tiền, một bên duy trì hệ sinh thái thanh toán bằng ngân sách đã tái phân bổ.
*Nội dung:* Decision matrix: Method (CI/BNPL/Wallet) × Mục tiêu (Growth/Retention-ecosystem) × Category ưu tiên × Nguồn ngân sách × Điều kiện áp dụng. Nêu rõ insight bổ sung: Wallet discount nên giảm dần cho khách đã trung thành, dồn cho segment thực sự "tiềm năng" (new_user/mid-frequency).
*Chart:* Bảng decision matrix (không phải chart, nhưng có thể kèm 1 small-multiple mini-chart minh hoạ ngân sách "trước/sau" theo 3 nhóm phương thức).

### Slide 9 — Cách triển khai: pilot trước khi scale
*Thông điệp chính:* Đây là đề xuất cần kiểm chứng bằng thử nghiệm, không phải cắt đại trà.
*Nội dung:* Rule engine theo ngưỡng seller-discount → giảm platform discount theo bậc (không cắt 100%) → loại trừ/giảm nhẹ hơn cho discount-sensitive user → đo lường trong X tuần → mở rộng nếu không giảm tần suất/conversion.
*Chart:* Timeline/step diagram (roadmap 3-4 giai đoạn: Pilot → Đo lường → Điều chỉnh → Scale).

### Slide 10 — Giới hạn & Next steps
*Thông điệp chính:* Đây là kết luận dựa trên correlation, không phải causal test — và một số mẫu còn nhỏ.
*Nội dung:* Thiếu seller_id, thiếu dữ liệu experiment/control, mẫu Fashion/Home Living nhỏ, pnl hiện chỉ là "Payment Services P&L" chứ chưa phải P&L toàn doanh nghiệp. Next steps: A/B test thiết kế ở slide 9, định nghĩa success metric cho cross-subsidy, mở rộng data seller-level nếu có thể.
*Chart:* Không cần chart — dùng bảng 2 cột "Đã biết / Cần thêm" hoặc icon-based checklist.
