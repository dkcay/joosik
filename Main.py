# Main file

import streamlit as st
import pandas as pd
import requests
import math

st.set_page_config(page_title="매크로 종합 대시보드", layout="wide")
# st_autorefresh(interval=60000, key="datarefresh")

st.markdown(
    """
    <style>
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.write("주식 상황 종합 (1분 단위 업데이트)")
st.markdown("---")


# ============================================================
## Variables
# ============================================================


high = True
low = False

metrics_config = {
    "WTI": ["🛢️ WTI 유가 ($)", 85, 80, high],
    "BRENT": ["🛢️ BRENT 유가 ($)", 90, 85, high],
    "USD_KRW": ["💵 원/달러 환율 (원)", 1400, 1350, high],
    "US10Y": ["📈 미국 10년물 국채금리 (%)", 4.7, 4.5, high],
    "VIX": ["미국 VIX, (풋옵션)", 20, 17, high],
    "NDQ100": ["📉 나스닥 100 선물 (%)", -1.0, -0.5, low],
    "KOSPI200": ["📉 코스피 200 야간선물 (%)", -2.0, -1.0, low],

}

toss_url_mapping = {
    "VIX": "https://www.tossinvest.com/indices/RGI..VIX",
    "USD_KRW": "https://www.tossinvest.com/indices/exchange-rate",
    "US10Y": "https://www.tossinvest.com/indices/ROB.US10YT-RR?tab=%EC%B1%84%EA%B6%8C",
    "WTI": "https://kr.investing.com/commodities/crude-oil",
    "NDQ100": "https://www.investing.com/indices/nq-100-futures",
    # 나중에 추가

    # 아직 다른 소스 사용
    "BRENT": None,
    "KOSPI200": "https://esignal.co.kr/kospi200-futures-night/",
}

# ============================================================
# Toss증권 실시간 데이터
# ============================================================

def get_toss_current(key):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Origin": "https://www.tossinvest.com",
        "Referer": "https://www.tossinvest.com/",
    }

    if key == "VIX":

        url = "https://wts-info-api.tossinvest.com/api/v1/index-prices/RGI..VIX"

        response = requests.get(
            url,
            headers=headers,
            timeout=5
        )

        response.raise_for_status()

        data = response.json()

        return float(data["result"]["close"])


    elif key == "USD_KRW":

        url = (
            "https://wts-info-api.tossinvest.com/"
            "api/v1/product/exchange-rate"
            "?buyCurrency=USD&sellCurrency=KRW"
        )

        response = requests.get(
            url,
            headers=headers,
            timeout=5
        )

        response.raise_for_status()

        data = response.json()

        return float(data["result"]["close"])

    elif key == "US10Y":

            url = (
                "https://wts-cert-api.tossinvest.com/"
                "api/v3/dashboard/wts/overview/indicator/mini-chart"
            )

            response = requests.get(
                url,
                headers=headers,
                timeout=5
            )

            response.raise_for_status()

            data = response.json()

            bonds = data["result"]["indexMap"]["채권"]

            for bond in bonds:
                if bond.get("code") == "ROB.US10YT-RR":
                    return float(bond["price"]["latestPrice"])

            raise ValueError("US10Y 데이터를 찾을 수 없습니다 (응답 구조 변경 가능성).")

    elif key == "WTI":

        url = (
            "https://wts-cert-api.tossinvest.com/"
            "api/v3/dashboard/wts/overview/indicator/mini-chart"
        )

        response = requests.get(
            url,
            headers=headers,
            timeout=5
        )

        response.raise_for_status()

        data = response.json()

        commodities = data["result"]["indexMap"]["원자재"]

        for item in commodities:
            if item.get("code") == "RFU.CLv1":
                return float(item["price"]["latestPrice"])

        raise ValueError("WTI 데이터를 찾을 수 없습니다.")


    elif key == "NDQ100":

        url = (
            "https://wts-cert-api.tossinvest.com/"
            "api/v3/dashboard/wts/overview/indicator/mini-chart"
        )

        response = requests.get(
            url,
            headers=headers,
            timeout=5
        )

        response.raise_for_status()

        data = response.json()

        indices = data["result"]["indexMap"]["주가지수"]

        for item in indices:
            if item.get("code") == "RFU.NQc1":
                base = float(item["price"]["basePrice"])
                latest = float(item["price"]["latestPrice"])
                return round((latest - base) / base * 100, 2)

        raise ValueError("NDQ100 데이터를 찾을 수 없습니다.")



    else:

        raise NotImplementedError(
            f"{key} Toss 데이터 소스를 아직 연결하지 않았습니다."
        )

# ============================================================
# Brent 유가
# ============================================================

def get_brent():

    # TODO:
    # Brent 데이터 소스 연결

    raise NotImplementedError(
        "BRENT 데이터 소스를 연결해야 합니다."
    )

# ============================================================
# KOSPI 200 야간선물
# ============================================================

def get_kospi200_night():

    raise NotImplementedError(
        "KOSPI200 야간선물 데이터 소스를 연결해야 합니다.")


# ============================================================
# CNN 공포탐욕지수
# ============================================================

def get_cnn_fear_greed():

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    }

    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"

    response = requests.get(url, headers=headers, timeout=5)
    response.raise_for_status()

    data = response.json()

    score = data["fear_and_greed"]["score"]
    rating = data["fear_and_greed"]["rating"]

    return round(float(score)), rating

# ============================================================
# 코스피 공탐지수 (feargreed.co.kr)
# ============================================================

def get_kospi_fear_greed():

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    }

    url = "https://feargree-api.vercel.app/api"

    response = requests.get(url, headers=headers, timeout=5)
    response.raise_for_status()

    data = response.json()

    score = data["kr"]["score"]
    label = data["kr"]["label"]

    return round(float(score)), label


# =========================================================
#  SECTION 1: 상단 실시간 데이터 표 (제목 / 현재가 / 경고등)
# =========================================================


table_data = []

with st.spinner("loading"):

    for key, info in metrics_config.items():

        name, t_1, t_2, is_high = info

        try:

            # ==================================================
            # Brent
            # ==================================================

            if key == "BRENT":

                price_val = get_brent()
                status = "⚪ 준비 중"

            # ==================================================
            # Toss증권
            # ==================================================

            else:
                if key == "KOSPI200":
                    price_val = get_kospi200_night()
                else:
                    price_val = get_toss_current(key)
                
                # ==================================================
                # 경고등
                # ==================================================

                if is_high:

                    if price_val >= t_1:
                        status = "🔴 심각"
                    elif price_val >= t_2:
                        status = "🟡 경계"
                    else:
                        status = "🟢 양호"

                else:

                    if price_val <= t_1:
                        status = "🔴 심각"
                    elif price_val <= t_2:
                        status = "🟡 경계"
                    else:
                        status = "🟢 양호"


            # ==================================================
            # 표에 추가
            # ==================================================

            table_data.append({
                "지표": name,
                "현재": price_val,
                "상태": status,
                "실시간 링크": toss_url_mapping.get(key)
            })


        except NotImplementedError:

            table_data.append({
                "지표": name,
                "현재": "-",
                "상태": "⚪ 준비 중",
                "실시간 링크": toss_url_mapping.get(key)
            })


        except Exception as e:

            st.write(f"{key} error: {e}")

            table_data.append({
                "지표": name,
                "현재": "로드 실패",
                "상태": "⚪ 미정",
                "실시간 링크": toss_url_mapping.get(key)
            })


# ============================================================
# DataFrame
# ============================================================

df = pd.DataFrame(table_data)

STATUS_BG = {
    "🔴": "#ff4d4a66",  # 심각 - 빨강
    "🟡": "#ffd10366",  # 경계 - 주황
    "🟢": "#32f53c66",  # 양호 - 초록
    "⚪": "#FFFEFE66",  # 준비중 - 회색
}

def highlight_current(row):
    icon = row["상태"][:1] if row["상태"] else ""
    color = STATUS_BG.get(icon, "")
    return ["", f"background-color: {color};", "", ""]

styled_df = df.style.apply(highlight_current, axis=1).format(precision=2)



col_left, col_mid, col_right = st.columns(
    [1.4, 1, 1],
    gap="medium",
    border=True
    )

with col_left:


    st.subheader("주요 지표")

    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "실시간 링크": st.column_config.LinkColumn(
                "실시간 링크",
                display_text="실시간 보기"
            )
        }
    )

    # ==============================
    # 공탐지수 / AI 종합의견
    # ==============================

    try:
        cnn_score, cnn_rating = get_cnn_fear_greed()
        cnn_display = f"{cnn_score} ({cnn_rating})"
    except Exception as e:
        cnn_display = "로드 실패"
        cnn_rating = None


    try:
        kospi_score, kospi_label = get_kospi_fear_greed()
        kospi_display = f"{kospi_score} ({kospi_label})"
    except Exception as e:
        kospi_display = "로드 실패"
        kospi_label = None


    with st.container(key="metrics_block"):

        st.markdown(
            """
            <style>
            .st-key-metrics_block {
                margin-top: -25px !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        def score_to_color(score: float) -> str:
            if score < 25:
                return "#e53935"
            if score < 45:
                return "#fb8c00"
            if score < 55:
                return "#fdd835"
            if score < 75:
                return "#81c784"
            return "#2e7d32"

        def build_gauge_html(score: float, label: str) -> str:
            score = max(0, min(100, float(score)))
            color = score_to_color(score)
            circumference = math.pi * 80
            filled = circumference * (score / 100)
            gap = circumference - filled
            return f'<svg viewBox="0 0 200 105" style="width:100%;max-width:170px;"><path d="M20,100 A80,80 0 0 1 180,100" fill="none" stroke="rgba(255,255,255,0.12)" stroke-width="14" stroke-linecap="round"/><path d="M20,100 A80,80 0 0 1 180,100" fill="none" stroke="{color}" stroke-width="14" stroke-linecap="round" stroke-dasharray="{filled:.1f} {gap:.1f}"/><text x="100" y="88" text-anchor="middle" font-size="40" font-weight="700" fill="#fff">{int(score)}</text></svg><div style="font-size:20px;color:#ccc;margin-top:-4px;">{label}</div>'

        def render_metric_box(title: str, value: str, link: str = None) -> None:
            link_overlay = f'<a href="{link}" target="_blank" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:1;"></a>' if link else ""
            st.markdown(
                f"""
                <div style="
                    position:relative;
                    display:flex;
                    flex-direction:column;
                    justify-content:center;
                    align-items:center;
                    height:204px;
                    text-align:center;
                    background-color: rgba(255,255,255,0.03);
                    border:1px solid rgba(250,250,250,0.2);
                    border-radius:8px;
                ">{link_overlay}<div style='font-size: 20px; font-weight: 600; line-height: 1.3;'>{title}</div><div style='font-size: 28px; font-weight: 600; margin-top: 12px;'>{value}</div></div>
                """,
                unsafe_allow_html=True
            )

        fear_col1, fear_col2, fear_col3 = st.columns(3)

        with fear_col1:
            cnn_value = build_gauge_html(cnn_score, cnn_rating) if cnn_rating else "로드 실패"
            render_metric_box("CNN 공탐지수", cnn_value, link="https://edition.cnn.com/markets/fear-and-greed")

        with fear_col2:
            kospi_value = build_gauge_html(kospi_score, kospi_label) if kospi_label else "로드 실패"
            render_metric_box("코스피 공탐지수", kospi_value, link="https://feargreed.co.kr/")

        with fear_col3:
            render_metric_box(
                "",
                "<div style='font-size:18px; font-weight:400; line-height:2; text-align:left; padding-left:20px; margin-top:-12px;'>"
                "0~24: 극단적 공포<br>"
                "25~44: 공포<br>"
                "45~55: 중립<br>"
                "56~75: 탐욕<br>"
                "76~100: 극단적 탐욕"
                "</div>"
            )

with col_mid:

    st.subheader("코스피200 야간선물")

    st.markdown("""
    <div style="
        height: 500px;
        overflow: hidden;
        border-radius: 12px;
    ">
        <iframe
            src="https://esignal.co.kr/kospi200-futures-night/"
            scrolling="no"
            style="
                width: 100%;
                height: 930px;
                border: none;
                transform: translateY(-430px);
            "
        ></iframe>
    </div>
    """, unsafe_allow_html=True)

with col_right:

    st.subheader("Warx 매크로 뉴스 / 유가 차트")
    
    st.components.v1.iframe(
        "https://warx.live/",
        height=500,
        scrolling=True
    )

#------------------------------------------------

def get_earnings_calendar(year_month: str):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Origin": "https://www.tossinvest.com",
        "Referer": "https://www.tossinvest.com/",
        "Content-Type": "application/json",
    }

    url = f"https://wts-cert-api.tossinvest.com/api/v4/calendar/monthly/{year_month}"

    response = requests.post(url, headers=headers, timeout=5)
    response.raise_for_status()

    data = response.json()
    events = data["result"]["events"]

    results = []

    for event in events:

        view = event.get("view") or {}
        title = view.get("title")

        if not title:
            continue

        date_str = event.get("date")  # "2026-06-02" 형태로 이미 옴

        if not date_str:
            continue

        # 시간 찾기: economicIndicatorValue 또는 stockEarnings 안에 있을 수 있음
        time_str = None

        econ = view.get("economicIndicatorValue")
        if econ and econ.get("time"):
            time_str = econ["time"]

        stock = event.get("stockEarnings")
        if stock and isinstance(stock, dict) and stock.get("time"):
            time_str = stock["time"]

        results.append({
            "date": date_str,
            "title": title,
            "group": event.get("group", ""),
            "time": time_str,  # "23:00:00" 또는 None
        })

    return results


def get_upcoming_earnings(limit: int = 200):
    from datetime import date

    today = date.today()
    year_months = []

    for i in range(0, 3):  # 이번 달 + 다음 달 + 다다음 달
        total = today.month - 1 + i
        y = today.year + total // 12
        m = total % 12 + 1
        year_months.append(f"{y}-{m:02d}")

    all_events = []
    for ym in year_months:
        try:
            all_events.extend(get_earnings_calendar(ym))
        except Exception:
            continue

    today_str = today.isoformat()
    upcoming = [e for e in all_events if e["date"] >= today_str]
    upcoming.sort(key=lambda x: (x["date"], x["time"] or ""))

    return upcoming[:limit]


col1, col2, col3 = st.columns(
    [1.4, 1, 1],
    gap="medium",
    border=True
    )


# ============================================================
# 코스피 투자자별 매매동향
# ============================================================

def format_krw_amount(amount: int) -> str:
    sign = "+" if amount >= 0 else "-"
    amount = abs(amount)

    eok = amount // 100_000_000
    jo = eok // 10_000
    eok_remain = eok % 10_000

    if jo > 0:
        return f"{sign}{jo}조 {eok_remain:,}억"
    else:
        return f"{sign}{eok_remain:,}억"


def get_kospi_trading_trend(days: int = 7):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Origin": "https://www.tossinvest.com",
        "Referer": "https://www.tossinvest.com/",
    }

    from datetime import date

    url = (
        "https://wts-info-api.tossinvest.com/"
        "api/v1/stock-infos/index/net-buying/daily"
        f"?code=KGG01P&count={days}&from={date.today().isoformat()}"
    )

    response = requests.get(url, headers=headers, timeout=5)
    response.raise_for_status()

    data = response.json()

    amounts = data["result"]["investorActivityAmounts"]

    results = []
    for row in amounts:
        results.append({
            "date": row.get("dt"),
            "individual": row.get("individualsNetBuying", 0),
            "foreigner": row.get("foreignersNetBuying", 0),
            "institution": row.get("institutionsNetBuying", 0),
        })

    return results



with col1:

    st.markdown(
        "<h3 style='text-align:center;'>코스피 현물/선물옵션/레버리지 매매동향</h3>",
        unsafe_allow_html=True
    )

    if "trend_tab" not in st.session_state:
        st.session_state.trend_tab = "현물"

    tabs = ["현물", "선물옵션", "레버리지"]
    btn_cols = st.columns(3)

    for i, label in enumerate(tabs):
        with btn_cols[i]:
            is_active = st.session_state.trend_tab == label
            clicked = st.button(
                label,
                key=f"trend_btn_{label}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            )
            if clicked:
                st.session_state.trend_tab = label
                st.rerun()

    trend_tab = st.session_state.trend_tab

    if trend_tab == "현물":

        try:
            trend_rows = get_kospi_trading_trend(days=7)

            table_html = (
                "<div style='padding:8px 16px;'>"
                "<div style='display:flex; font-weight:600; font-size:16px; color:#999; "
                "border-bottom:1px solid rgba(255,255,255,0.2); padding-bottom:8px;'>"
                "<div style='flex:1;'>날짜</div>"
                "<div style='flex:1; text-align:right;'>개인</div>"
                "<div style='flex:1; text-align:right;'>외국인</div>"
                "<div style='flex:1; text-align:right;'>기관</div>"
                "</div>"
            )

            for row in trend_rows:
                def colored(v):
                    color = "#e53935" if v >= 0 else "#4a7fff"
                    return f"<span style='color:{color};'>{format_krw_amount(v)}</span>"

                table_html += (
                    "<div style='display:flex; font-size:16px; padding:8px 0; "
                    "border-bottom:1px solid rgba(255,255,255,0.08);'>"
                    f"<div style='flex:1;'>{row['date']}</div>"
                    f"<div style='flex:1; text-align:right;'>{colored(row['individual'])}</div>"
                    f"<div style='flex:1; text-align:right;'>{colored(row['foreigner'])}</div>"
                    f"<div style='flex:1; text-align:right;'>{colored(row['institution'])}</div>"
                    "</div>"
                )

            table_html += "</div>"

        except Exception as e:
            table_html = "<div style='text-align:center; padding:40px;'>로드 실패</div>"

        st.markdown(table_html, unsafe_allow_html=True)

    else:

        st.markdown(
            f"<div style='text-align:center; padding:60px 0; color:#888;'>{trend_tab} 데이터 준비중입니다</div>",
            unsafe_allow_html=True
        )


with col2:

    st.markdown(
        "<h3 style='text-align:center;'>AI 종합 의견</h3>",
        unsafe_allow_html=True
    )

with col3:

    st.markdown(
        "<h3 style='text-align:center;'><a href='https://www.tossinvest.com/calendar' target='_blank' style='color:inherit; text-decoration:none;'>실적발표 일정</a></h3>",
        unsafe_allow_html=True
    )

    try:
        from datetime import date as date_cls
        today_str = date_cls.today().isoformat()

        earnings_list = get_upcoming_earnings(limit=200)

        earnings_html = ""
        last_date = None

        for e in earnings_list:

            if e["date"] != last_date:
                if last_date is not None:
                    earnings_html += "<hr style='margin:8px 0; border-color:rgba(255,255,255,0.15);'>"

                if e["date"] == today_str:
                    earnings_html += f"<div style='font-weight:700; font-size:20px; color:#4caf50; margin-top:6px;'>{e['date']} (오늘)</div>"
                else:
                    earnings_html += f"<div style='font-weight:600; font-size:16px; color:#fdd835; margin-top:6px;'>{e['date']}</div>"

                last_date = e["date"]

            time_display = e["time"][:5] if e["time"] else ""
            time_suffix = f" [{time_display}]" if time_display else ""
            earnings_html += f"<div style='padding:3px 0 3px 8px; font-size:14px;'>{e['title']}{time_suffix}</div>"

        if not earnings_html:
            earnings_html = "다가오는 일정 없음"

    except Exception as e:
        earnings_html = "로드 실패"

    st.markdown(
        f"<div style='text-align:left; padding:8px 16px; max-height:500px; overflow-y:auto;'>{earnings_html}</div>",
        unsafe_allow_html=True
    )

# 추가로 구현할 것들


# 3. 코스피 주간 선물옵션 매매동향
# 4. 선물 미결제약정 추이 그래프
# 5. 개인, 외인 레버리지, 인버스 포지션 (기관은 유동성공급자라 제외, 유명 15개 레버리지 데이터 종합) (kodex 레버리지, kodex200 선물인버스2x등등)
# 6. polymarket 주요 베팅 현황 (유가 등)

# 8. AI종합 의견 Strong Sell / Sell / Neutral(Hold) / Buy / Strong Buy
# 9. 데이터 자동 연동되는 AI채팅. (Claud, Chatgpt등 연결)


#완료
# 1. 실적발표 일정
# 2. 코스피 현물 매매동향

# 7. warx, sbh news등 종합 뉴스 웹에서 주요 macro 뉴스 리스트 하기
