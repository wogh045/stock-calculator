import streamlit as st
import yfinance as yf

# 웹 페이지 기본 설정
st.set_page_config(page_title="주식 가치평가 종합 계산기", layout="centered", page_icon="📈")

st.title("📊 주식 가치평가 종합 계산기")

# PER, PBR 개념 요약 (사용자가 원할 때만 펼쳐보게 숨김 처리)
with st.expander("💡 PER과 PBR 개념 요약 보기 (클릭해서 펼치기)"):
    st.markdown("""
    **1. PER (주가수익비율) : "이 회사가 돈을 버는 능력에 비해 주가가 적당한가?"**
    - **계산법:** 현재 주가 ÷ 1주당 순이익(EPS)
    - **의미:** 낮을수록 수익 대비 주가가 저평가되어 있으며, 투자 원금을 회수하는 데 걸리는 기간(년)을 의미하기도 합니다.

    **2. PBR (주가순자산비율) : "이 회사가 가진 재산에 비해 주가가 적당한가?"**
    - **계산법:** 현재 주가 ÷ 1주당 순자산(BPS)
    - **의미:** 1 미만이면 회사가 가진 장부상 순재산보다도 주가가 싸게 거래되는 '저평가' 상태를 뜻합니다.
    """)

# 두 개의 화면을 탭으로 나누기
tab1, tab2 = st.tabs(["🔍 실시간 종목 검색", "🎛️ 가상 시뮬레이터 (직접 조절)"])

# ----- 탭 1: 실시간 종목 검색 -----
with tab1:
    st.subheader("야후 파이낸스 실시간 데이터 연동")
    ticker_input = st.text_input("종목 코드 입력 (예: 애플은 AAPL, 삼성전자는 005930.KS)", value="AAPL")

    if st.button("🔄 실시간 데이터 불러오기 / 새로고침"):
        if ticker_input:
            with st.spinner('실시간 데이터를 가져오는 중입니다...'):
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
                        col1.metric("실시간 주가", f"{price:,.2f}")
                        col2.metric("직전 EPS (주당순이익)", f"{eps:,.2f}")
                        col3.metric("직전 BPS (주당순자산)", f"{bps:,.2f}")
                        
                        st.divider()
                        
                        st.markdown("##### 🔍 가치 평가 결과")
                        col4, col5 = st.columns(2)
                        
                        if per: col4.metric("✅ PER (주가수익비율)", f"{per:.2f} 배")
                        else: col4.metric("✅ PER", "적자 기업")
                            
                        if pbr: col5.metric("✅ PBR (주가순자산비율)", f"{pbr:.2f} 배")
                        else: col5.metric("✅ PBR", "자본 잠식")
                    else:
                        st.warning("⚠️ 야후 파이낸스에서 해당 종목의 재무 데이터를 완전히 제공하지 않습니다.")
                except Exception as e:
                    st.error("오류가 발생했습니다. 종목 코드가 정확한지 확인해 주세요.")
        else:
            st.warning("종목 코드를 입력해 주세요.")

# ----- 탭 2: 가상 시뮬레이터 (슬라이더 바) -----
with tab2:
    st.subheader("주가, 이익, 자산을 직접 움직여보세요!")
    st.write("아래의 바(Slider)를 좌우로 조절하거나 숫자를 직접 기입하면 하단의 PER, PBR 결과가 실시간으로 변합니다.")
    
    # 슬라이더(바) 및 숫자 입력 UI 구성
    sim_price = st.slider("💰 가상의 현재 주가 (원)", min_value=1000, max_value=200000, value=50000, step=1000)
    sim_eps = st.slider("📈 1주당 순이익 (EPS)", min_value=100, max_value=20000, value=5000, step=100)
    sim_bps = st.slider("🏦 1주당 순자산 (BPS)", min_value=1000, max_value=150000, value=50000, step=1000)
    
    # 조절된 값으로 PER, PBR 자동 계산
    sim_per = sim_price / sim_eps if sim_eps > 0 else 0
    sim_pbr = sim_price / sim_bps if sim_bps > 0 else 0
    
    st.divider()
    st.markdown("#### 🔍 시뮬레이션 결과")
    
    # 결과 나란히 배치
    col_sim1, col_sim2 = st.columns(2)
    col_sim1.metric("✅ 계산된 PER", f"{sim_per:.2f} 배")
    col_sim2.metric("✅ 계산된 PBR", f"{sim_pbr:.2f} 배")
    
    # 값의 변화에 따른 동적 해석 문구 제공
    st.info(f"**해석:** 설정하신 값에 따르면, 이 기업에 투자한 원금을 순이익으로 모두 회수하는 데 이론적으로 **{sim_per:.1f}년**이 걸립니다. 또한 주가가 회사가 가진 순수 재산에 비해 **{sim_pbr:.1f}배**의 가격으로 시장에서 거래되고 있음을 의미합니다.")
