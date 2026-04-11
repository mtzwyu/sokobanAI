import math
import random

def simulated_annealing(initial_state, get_neighbors, get_heuristic,
                        initial_temperature=None, cooling_rate=0.97, min_temperature=0.1,
                        max_iterations_per_temp=10):
    """
    Thuật toán Tôi luyện mô phỏng (Simulated Annealing).
    Đúng theo pseudocode Kirkpatrick et al. (1983) / GA Tech OMSCS 7641:

        S ← S0,  T ← T0
        While T > T_min:
            For i in range(N):
                S' ← random_neighbor(S)           # Perturb ngẫu nhiên
                ΔE = E(S') − E(S)
                If ΔE ≤ 0:    S ← S'              # Luôn chấp nhận cải thiện
                Else:
                    α ← random(0,1)
                    If α ≤ e^(−ΔE/T):  S ← S'    # Chấp nhận có xác suất
            T ← T × cooling_rate

    Cải tiến thực tế:
    - T0 TỰ ĐỘNG: T0 = initial_h / 200 → scale phù hợp với 1 box hay 20 box
      * initial_h ~ 3000 (1 box) → T0 ≈ 15: ΔE_player=5 có P=e^(-0.33)=0.72 ✅
      * initial_h ~ 20000 (20 box) → T0 ≈ 100: ΔE_player=5 có P=e^(-0.05)=0.95 ✅
      * Với bất kỳ T0 nào: ΔE_box=1000 → P ≈ 0 (không đẩy hộp ra khỏi đích)
    - DRIFT CONTROL: nếu SA trôi > 50% so với best → reset về best
      (ngăn SA tích lũy H3 penalty qua hàng nghìn bước nhỏ → H=204000)
    """
    current_state = initial_state
    current_h = get_heuristic(current_state)
    path = []

    best_state = current_state
    best_h = current_h
    best_path = []

    # T0 tự động theo quy mô bài toán — căn cứ trên Excel:
    # - Player-level ΔE ≈ 0.55-1.0 (từ bước 1→2, 5→6 trong Excel)
    # - Công thức: T0 = -ΔE / ln(P) với ΔE=1, P=0.90 → T0 ≈ 9.5 ≈ 10
    # - Clamp [5, 20]: tránh quá lạnh (không khám phá) hoặc quá nóng (lang thang vô hướng)
    # - Với map 20 box (H≈431028): T0=10 → e^(-0.55/10)=0.946 (chấp nhận player moves tự do)
    #                                         e^(-1000/10)≈0    (không bao giờ đẩy hộp ra đích)
    if initial_temperature is None:
        temperature = max(5.0, min(20.0, current_h / 50000.0))
    else:
        temperature = initial_temperature

    # Drift limit: tuyệt đối 500 (< H4=1000/box) → SA không thể drift vào vùng box-off-goal
    drift_limit = min(500.0, current_h * 0.001) if current_h > 0 else 500.0

    while temperature > min_temperature:
        for _ in range(max_iterations_per_temp):
            if best_h == 0:
                break

            neighbors = get_neighbors(current_state)
            if not neighbors:
                break

            # Perturb: chọn NGẪU NHIÊN 1 hàng xóm (đặc trưng SA)
            action, next_state = random.choice(neighbors)
            next_h = get_heuristic(next_state)

            delta_e = next_h - current_h

            if delta_e <= 0:
                # ΔE ≤ 0: cải thiện hoặc bằng → luôn chấp nhận (S ← S')
                current_state = next_state
                current_h = next_h
                path.append(action)
            else:
                # ΔE > 0: tệ hơn → chấp nhận với P = e^(−ΔE/T)
                # Python an toàn: e^(-1000/T) → 0.0 tự động (không cần cap)
                acceptance_prob = math.exp(-delta_e / temperature)
                if random.random() <= acceptance_prob:
                    current_state = next_state
                    current_h = next_h
                    path.append(action)

            # Ghi nhớ best
            if current_h < best_h:
                best_h = current_h
                best_state = current_state
                best_path = list(path)

            # DRIFT CONTROL: SA trôi quá xa best → reset về best
            # Ngăn SA tích lũy H3 penalty dần → H=204000 sau nhiều bước nhỏ
            if current_h > best_h + drift_limit:
                current_state = best_state
                current_h = best_h
                path = list(best_path)

        if best_h == 0:
            break

        # Decrement T (làm nguội hàm mũ)
        temperature *= cooling_rate

    return best_state, best_path
