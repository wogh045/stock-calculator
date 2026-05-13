import streamlit as st
import yfinance as yf

# 웹 페이지 기본 설정
st.set_page_config(page_title="주식 가치평가 종합 계산기", layout="centered", page_icon="📈")

# 실시간 환율 가져오기 (매번 불러오면 느려지므로 캐싱 처리)
@st.cache_data(ttl=3600)
def get_exchange_rate():
    try:
        return yf.Ticker("KRW=X").history(period="1d")['Close'].iloc[-1]
    except:
        return 1350.0  # 환율 로드 실패 시 임시 기준값

usd_krw = get_exchange_rate()

# 고평가/저평가 판별 함수
def evaluate_per(per):
    if per is None or per <= 0: return "⚫ 평가 불가 (적자)"
    elif per < 10: return "🟢 저평가 (10 미만)"
    elif per <= 20: return "🟡 적정가 (10~20)"
    else: return "🔴 고평가 (20 초과)"

def evaluate_pbr(pbr):
    if pbr is None or pbr <= 0: return "⚫ 평가 불가 (자본잠식)"
    elif pbr < 1: return "🟢 저평가 (1 미만)"
    elif pbr <= 1.5: return "🟡 적정가 (1~1.5)"
    else: return "🔴 고평가 (1.5 초과)"

st.title("📊 주식 가치평가 종합 계산기")
st.info(f"💡 현재 적용된 실시간 원/달러 환율: 약 **{usd_krw:,.1f}원**")

tab1, tab2 = st.tabs(["🔍 실시간 종목 검색", "🎛️ 가상 시뮬레이터 (직접 조절)"])

# ----- 탭 1: 실시간 종목 검색 -----
with tab1:
    ticker_input = st.text_input("종목 코드 입력 (예: 애플은 AAPL, 삼성전자는 005930.KS)", value="000660.KS") # 하이닉스 기본값

    if st.button("🔄 실시간 데이터 불러오기 / 새로고침"):
        if ticker_input:
            with st.spinner('데이터를 가져오는 중입니다...'):
                try:
                    stock = yf.Ticker(ticker_input.strip().upper())
                    info = stock.info
                    
                    price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
                    eps = info.get('trailingEps')
                    bps = info.get('bookValue')
                    name = info.get('longName', ticker_input.upper())
                    
                    if price and eps and bps:
                        per = price / eps if eps > 0 else None
                        pbr = price / bps if bps > 0 else None
                        
                        st.markdown(f"#### 🏢 {name}")
                        col1, col2, col3 = st.columns(3)
                        
                        # 한국 주식이면 원화->달러, 미국 주식이면 달러->원화 환산
                        if ".KS" in ticker_input.upper() or ".KQ" in ticker_input.upper():
                            col1.metric("실시간 주가", f"{price:,.0f} 원", f"약 ${price/usd_krw:,.2f}", delta_color="off")
                        else:
                            col1.metric("실시간 주가", f"${price:,.2f}", f"약 {price*usd_krw:,.0f} 원", delta_color="off")
                            
                        col2.metric("직전 EPS", f"{eps:,.2f}")
                        col3.metric("직전 BPS", f"{bps:,.2f}")
                        
                        st.divider()
                        st.markdown("##### 🔍 가치 평가 결과")
                        col4, col5 = st.columns(2)
                        
                        per_text = f"{per:.2f} 배" if per else "계산 불가"
                        pbr_text = f"{pbr:.2f} 배" if pbr else "계산 불가"
                        
                        col4.metric(f"✅ PER ({evaluate_per(per)})", per_text)
                        col5.metric(f"✅ PBR ({evaluate_pbr(pbr)})", pbr_text)
                    else:
                        st.warning("⚠️ 재무 데이터를 완전히 제공하지 않는 종목입니다.")
                except Exception as e:
                    st.error("오류가 발생했습니다. 종목 코드를 확인해 주세요.")

# ----- 탭 2: 가상 시뮬레이터 (슬라이더 및 수기 입력) -----
with tab2:
    st.subheader("주가, 이익, 자산을 직접 움직여보세요!")
    st.write("💡 **Tip:** 바 위의 숫자를 클릭하면 키보드로 정확한 금액을 직접 입력할 수 있습니다.")
    
    # 최댓값을 500만원(5,000,000)으로 확장
    sim_price = st.slider("💰 가상의 현재 주가 (원)", min_value=1000, max_value=5000000, value=180000, step=1000)
    st.caption(f"💵 달러 환산 금액: 약 **${sim_price/usd_krw:,.2f}**")
    
    sim_eps = st.slider("📈 1주당 순이익 (EPS)", min_value=100, max_value=500000, value=20000, step=500)
    sim_bps = st.slider("🏦 1주당 순자산 (BPS)", min_value=1000, max_value=5000000, value=150000, step=1000)
    
    sim_per = sim_price / sim_eps if sim_eps > 0 else 0
    sim_pbr = sim_price / sim_bps if sim_bps > 0 else 0
    
    st.divider()
    st.markdown("#### 🔍 시뮬레이션 결과")
    
    col_sim1, col_sim2 = st.columns(2)
    col_sim1.metric(f"✅ 예상 PER ({evaluate_per(sim_per)})", f"{sim_per:.2f} 배")
    col_sim2.metric(f"✅ 예상 PBR ({evaluate_pbr(sim_pbr)})", f"{sim_pbr:.2f} 배")
