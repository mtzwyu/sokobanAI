# Bộ 7 Sơ đồ và Diễn giải thuật toán Hill Climbing

Tài liệu này tổng hợp **toàn bộ 7 biến thể** của thuật toán **Hill Climbing (Leo đồi)** được áp dụng trong dự án tìm kiếm và giải quyết Sokoban. Tài liệu bao gồm sơ đồ luồng (Flowchart) và phần giải thích chi tiết cơ chế hoạt động của từng thuật toán.

---

## PHẦN 1: NHÓM BASIC SEARCH (TÌM KIẾM CƠ BẢN)

### 1. Simple Hill Climbing (`simple_hill_climbing.py`)

Thuật toán Leo đồi đơn giản tìm kiếm một cách tuần tự. Ngay khi nó nhìn thấy một "hàng xóm" (hướng đi) có giá trị cực tiểu (heuristic nhỏ hơn) so với trạng thái hiện tại, nó lập tức chọn bước đi đó mà không cần quan tâm đến các hàng xóm còn lại.

```mermaid
flowchart TD
    Start(["Bắt đầu Simple HC"]) --> Init["current_state = initial<br>current_h = h(initial)"]
    Init --> LoopCheck{"Đạt max_iterations?"}
    
    LoopCheck -- Có --> End(["Kết thúc, trả về kết quả"])
    LoopCheck -- Không --> GoalCheck{"current_h == 0?"}
    GoalCheck -- Có --> End
    
    GoalCheck -- Không --> GetNeighbors["Sinh các trạng thái kề"]
    GetNeighbors --> FoundBetterFalse["Đặt found_better = False"]
    
    FoundBetterFalse --> LoopNeighbors["Duyệt TUẦN TỰ từng hàng xóm:<br>Tính next_h"]
    LoopNeighbors --> IsBetter{"next_h < current_h?"}
    
    IsBetter -- Có --> UpdateState["Cập nhật current_state = next_state<br>Lưu hành động<br>found_better = True"]
    UpdateState --> BreakInner["Dừng duyệt hàng xóm (break)"]
    IsBetter -- Không --> ContinueNeighbors{"Còn hàng xóm?"}
    
    ContinueNeighbors -- Còn --> LoopNeighbors
    ContinueNeighbors -- Hết --> BreakInner
    
    BreakInner --> CheckFound{"found_better == True?"}
    CheckFound -- "Tính trạng thái mới" --> LoopCheck
    CheckFound -- "Kẹt (Local Minima) Khởi Động" --> End
```

**Diễn giải chi tiết:**
- **Đầu vào:** Trạng thái bắt đầu.
- **Vòng lặp:** Bắt đầu tính toán từng hàng xóm của trạng thái hiện tại.
- **Tiêu chí chọn:** Hàng xóm đầu tiên có `next_h < current_h` sẽ được coi là điểm đến tiếp theo.
- **Điểm yếu:** Dễ kẹt nhánh, hướng đi rất phụ thuộc vào thứ tự duyệt mảng sinh ra bởi `get_neighbors()`.

---

### 2. Steepest Ascent Hill Climbing (`steepest_ascent.py`)

Được gọi là "Leo đồi dốc đứng". Khác với Simple HC, thuật toán này cẩn thận sinh ra *toàn bộ* các hàng xóm, đánh giá *tất cả* chung với nhau và CHỈ CHỌN 1 TRẠNG THÁI TỐT NHẤT trong số đó.

```mermaid
flowchart TD
    Start(["Bắt đầu Steepest Ascent HC"]) --> Init["current_state = initial"]
    Init --> LoopCheck{"Đạt max_iterations?"}
    LoopCheck -- Hết --> End(["Kết thúc"])
    
    LoopCheck -- Chưa --> GetNeighbors["Lấy tất cả hàng xóm"]
    
    GetNeighbors --> EvaluateAll["Đánh giá LƯỢT toàn bộ hàng xóm:<br>Tìm best_next_state có best_h nhỏ nhất"]
    EvaluateAll --> IsBetterOverall{"best_h < current_h?"}
    
    IsBetterOverall -- Có --> UpdateState["current_state = best_next_state<br>Thêm vào đường đi"]
    IsBetterOverall -- "Không (Local Minima)" --> End
    
    UpdateState --> LoopCheck
```

**Diễn giải chi tiết:**
- Lấy toàn bộ hàng xóm xung quanh trạng thái hiện tại.
- Cho biến `best_h = Vô_cực`. So sánh heuristic của tất cả hàng xóm, giữ lại cái nhỏ nhất.
- Cuối cùng lấy cái nhỏ nhất đem so với vị trí hiện tại. 
- Ưu điểm là luôn đi hướng dốc nhất, nhưng tốn chi phí đánh giá mọi node kề. Kẹt Local Minima khi không có hướng nào thẳng đứng hơn.

---

## PHẦN 2: NHÓM STOCHASTIC SEARCH (TÌM KIẾM NGẪU NHIÊN)

### 3. Stochastic Hill Climbing (`stochastic_hc.py`)

Đây là biến thể Stochastic chuẩn, không phải chọn tất cả đồ tốt rồi lấy cái tốt nhất, mà nó liệt kê TẤT CẢ các ngã rẽ "tốt hơn hiện tại", sau đó **BỐC THĂM NGẪU NHIÊN** 1 ngã rẽ.

```mermaid
flowchart TD
    Start(["Bắt đầu Stochastic Hill Climbing"])
    Init["Khởi tạo:<br>current_state = initial_state<br>current_h = get_heuristic..."]
    
    LoopStart{"Vòng lặp:<br>Đã đạt max_iterations?"}
    GoalCheck{"current_h == 0?<br>(Đã đến đích?)"}
    
    GetNeighbors["Lấy danh sách các trạng thái kề<br>neighbors = get..."]
    
    FilterStart["better_neighbors = rỗng"]
    FilterLoop["Duyệt qua từng hàng xóm:<br>Tính next_h<br>Nếu next_h < current_h -> Thêm vào better_neighbors"]
    
    MinimaCheck{"better_neighbors<br>có rỗng không?"}
    
    RandomChoice["chosen_state = random.choice(better_neighbors)"]
    
    UpdateState["Cập nhật:<br>current_state = chosen_state<br>Lưu action vào path"]
    
    End(["Kết thúc thuật toán.<br>Trả về current_state, path"])

    Start --> Init
    Init --> LoopStart    
    LoopStart -- "Đã đạt giới hạn (max)" --> End
    LoopStart -- "Chưa đạt giới hạn" --> GoalCheck
    GoalCheck -- "Có (Tìm thấy đích)" --> End
    GoalCheck -- "Không" --> GetNeighbors
    GetNeighbors --> FilterStart
    FilterStart --> FilterLoop
    FilterLoop --> MinimaCheck    
    MinimaCheck -- "Có rỗng (Local Minima)" --> End
    MinimaCheck -- "Không rỗng" --> RandomChoice
    RandomChoice --> UpdateState
    UpdateState --> LoopStart
```

**Diễn giải chi tiết:**
- Duyệt và đánh giá mọi hàng xóm.
- Chỉ giữ lại những hàng xóm tốt hơn (`next_h < current_h`) vào kho `better_neighbors`.
- Ra quyết định dựa trên tính ngẫu nhiên `random.choice(better_neighbors)`. Xác suất có thể giúp thuật toán không đi vào lối mòn (có thể nhảy sang hướng khác Steepest Ascent).

---

### 4. First-Choice Hill Climbing (`first_choice_hc.py`)

Đây là con lai giữa Stochastic và Simple. Nó cần tính ngẫu nhiên, nhưng ngại đánh giá hết hàng xóm (nếu hàng xóm có hàng ngàn Node sẽ mất thời gian). Vì vậy, nó "**XÁO TRỘN ĐỘI HÌNH**" thay vì đánh giá tất cả.

```mermaid
flowchart TD
    Start(["Bắt đầu First Choice HC"]) --> Init["current_state = initial<br>current_h = h(initial)"]
    Init --> LoopCheck{"Đạt max_iterations?"}
    
    LoopCheck -- Có --> End(["Kết thúc, trả về kết quả"])
    LoopCheck -- Không --> GoalCheck{"current_h == 0?"}
    GoalCheck -- Có --> End
    
    GoalCheck -- Không --> GetNeighbors["Sinh các trạng thái kề"]
    GetNeighbors --> Shuffle["Xáo trộn NGẪU NHIÊN danh sách kề<br>random.shuffle(neighbors)"]
    
    Shuffle --> LoopNeighbors["Duyệt từng hàng xóm:<br>Tính next_h"]
    LoopNeighbors --> IsBetter{"next_h < current_h?"}
    
    IsBetter -- Có --> UpdateState["Cập nhật current_state<br>Dừng duyệt (break)"]
    IsBetter -- Không --> ContinueNeighbors{"Còn hàng xóm?"}
    ContinueNeighbors -- Còn --> LoopNeighbors
    ContinueNeighbors -- Hết --> CheckMinima{"Tìm được hướng tốt?"}
    
    UpdateState --> LoopCheck
    CheckMinima -- "Không (Local Minima)" --> End
```

**Diễn giải chi tiết:**
- Lấy danh sách hàng xóm ra, trước khi duyệt sẽ bị `random.shuffle()` xáo tung lên.
- Quét lần lượt (giống hệ Simple HC), hễ gặp Node đàu tiên `next < current` là chốt hạ luôn, đi qua đó ngay lập tức bỏ qua hết những Node phía sau.
- Hiệu suất cực nhanh với không gian sinh Node rộng.

---

## PHẦN 3: NHÓM ESCAPE LOCAL MINIMA (THOÁT KẸT)

### 5. Random Restart Hill Climbing (`random_restart_hc.py`)

Bản chất thuật toán này không thay đổi cách đi, nó chạy thuật toán cơ bản. NHƯNG nếu bị kẹt (Local Minima), thay vì kết thúc, nó sẽ **QUĂNG NGƯỜI CHƠI SANG MỘT VỊ TRÍ MỚI HOÀN TOÀN TỪ ĐẦU** trên bản đồ và thử chạy lại.

```mermaid
flowchart TD
    Start(["Bắt đầu Random Restart"]) --> InitGlobal["Lưu best_overall = initial"]
    InitGlobal --> LoopRestart{"Vòng lặp Restart<br>(max_restarts)"}
    
    LoopRestart -- Đủ số lần --> End(["Trả về best_overall"])
    LoopRestart -- Chưa --> InitLocal["current_state = current_start_state"]
    
    InitLocal --> RunHC["Chạy vòng lặp Simple Hill Climbing<br>từ current_state"]
    RunHC --> CheckHCResult["HC dừng vì kẹt Local Minima<br>hoặc H=0"]
    
    CheckHCResult --> UpdateGlobal{"current_h < best_overall_h?"}
    UpdateGlobal -- Có --> DoUpdateGlobal["Cập nhật best_overall"]
    UpdateGlobal -- Không --> NextStep
    DoUpdateGlobal --> NextStep
    
    NextStep{"Đích (H=0)?"}
    NextStep -- Phải --> End
    NextStep -- Không phải --> GenRandom["Tạo random_initial_state mới"]
    
    GenRandom --> UpdateStart["current_start_state = new_state"]
    UpdateStart --> LoopRestart
```

**Diễn giải chi tiết:**
- Chạy Simple/Steepest HC từ điểm xuất phát sinh ra.
- Nếu lọt hố (kẹt), kết quả điểm kẹt đó được so sánh ghi nhận vào Kỉ lục thế giới `best_overall_h`.
- Trò chơi ép `initial_state` bốc hơi và spawn ra bàn mới (nếu hàm Random_state khả dụng). Tính năng này phù hợp các bài toán dạng N-Queens hơn Sokoban (vì Sokoban phụ thuộc cấu trúc tường cố định).
- Trả về kỷ lục leo xa nhất sau N vòng lặp.

---

### 6. Jumping Hill Climbing (`jumping_hc.py`)

Đây là một thuật toán thực dụng. Đang chạy bình thường theo kiểu Steepest Ascent, tự nhiên hết đường vì kẹt cục bộ. Thế thì nó thử xin "1 CÚ NHẢY XA" ngay tại nơi đang đứng ra các vùng chưa biết. Nếu nhảy qua được hố hẹp thì đi bộ tiếp.

```mermaid
flowchart TD
    Start(["Bắt đầu Jumping HC"]) --> Init["current_state = initial"]
    Init --> LoopCheck{"Vòng lặp chính"}
    LoopCheck --> RunSteepest["Tìm hàng xóm tốt nhất (Steepest Ascent)"]
    
    RunSteepest --> IsBetter{"Tìm được hương < current_h?"}
    IsBetter -- Có --> Move["Đi tiếp (cập nhật current_state)"]
    Move --> LoopCheck
    
    IsBetter -- Không --> LocalMinima["Kẹt Local Minima"]
    LocalMinima --> LoopJump{"Thử nhảy (tối đa 3 lần)"}
    
    LoopJump -- Hết 3 lần --> End(["Đầu hàng, Trả về"])
    LoopJump -- Còn thử được --> TryJump["Gọi generate_random_state_fn(current)"]
    
    TryJump --> ValidJump{"Nhảy hợp lệ & Không deadlock?"}
    ValidJump -- Không --> LoopJump
    ValidJump -- Có --> AcceptJump["Gắn current_state = vị trí nhảy<br>Ghi lại đường nhảy"]
    
    AcceptJump --> LoopCheck
```

**Diễn giải chi tiết:**
- Duyệt bình thường theo Steepest Ascent HC để tận dụng điệu leo chắc chắn nhất.
- Kẹt hố thì không đầu hàng. Sử dụng hàm nhảy nội bộ từ state. Tránh deadlock.
- Nếu qua được deadlock bằng Random Move thì reset lại quy trình dò đường từ vị trí mới tiếp đất. Không qua được thì đành chết hẳn.

---

### 7. Backtracking Hill Climbing (`backtracking_hc.py`)

"Lạc đường thì lùi một bước chớ có vội luống cuống". Thuật toán lưu ngã rẽ vào Stack. Khi đâm vào Local Minima (ngõ cụt), nó nhớ lại cách đây vài chục bước còn cái hành lang chẻ sang trái chưa rẽ, nó sẽ LÙI (pop stack) qua đó ngó xem sao.

```mermaid
flowchart TD
    Start(["Bắt đầu Backtracking HC"]) --> Init["stack = trạng thái đầu, kề sắp xếp H+<br>visited = set()<br>best_overall = ban đầu"]
    
    Init --> LoopStack{"Stack còn phần tử?"}
    
    LoopStack -- Rỗng --> End(["Trả về best_overall"])
    LoopStack -- Còn --> PeekStack["Lấy đỉnh Stack (curr_state, branches)"]
    
    PeekStack --> BranchEmpty{"branches trống rỗng?"}
    
    BranchEmpty -- "Có (Hết đường rẽ)" --> PopStack["Loại đỉnh (stack.pop)<br>Lùi quỹ đạo (-1 bước)"]
    PopStack --> LoopStack
    
    BranchEmpty -- Không --> PopBranch["Lấy nhánh tốt nhất tiếp theo<br>next_state = branches.pop(0)"]
    
    PopBranch --> CheckVisited{"next_state trong visited?"}
    CheckVisited -- Có --> PeekStack
    
    CheckVisited -- Không --> VisitNode["visited.add(next_state)"]
    VisitNode --> GetNewBranches["Lấy kề của next_state<br>Sắp xếp theo Heuristic"]
    GetNewBranches --> AppendStack["stack.append(next_state, new_branches)"]
    
    AppendStack --> UpdateGlobal{"Cập nhật Record holder<br>best_overall"}
    UpdateGlobal --> CheckGoal{"Đã tìm thấy đích (H=0)?"}
    CheckGoal -- Có --> End
    CheckGoal -- Không --> LoopStack
```

**Diễn giải chi tiết:**
- Kết hợp tìm kiếm ưu tiên (DFS) với hàm đánh giá `get_heuristic()`. Tại mỗi ngã rẽ đồ thị, chọn rẽ vào hướng có Heuristic thấp nhất đầu tiên.
- Khúc rẽ chưa dạo được đẩy vào `branches` trên Stack. Kẹt đường thì loại vị trí này, quay lại cái đỉnh ở dưới Stack, móc ngã 2, ngã 3 ra và đi tiếp.
- `visited = set()` cản đường nó lặp lại một vùng đã đi, ngăn đi vòng tròn vô hạn. Phù hợp nhất để giải quyết triệt để Local Maxima/Minima ở mức sơ đồ tìm kiếm.
