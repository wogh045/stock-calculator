import streamlit as st
import yfinance as yf

# 웹 페이지 기본 설정
st.set_page_config(page_title="실시간 주식 가치평가 계산기", layout="centered", page_icon="📈")

st.title("📊 실시간 PER & PBR 계산기")
st.write("야후 파이낸스 데이터를 기반으로 실시간 주가와 기업 가치를 평가합니다.")

# 종목 코드 입력란
ticker_input = st.text_input("종목 코드 입력 (예: 애플은 AAPL, 삼성전자는 005930.KS)", value="AAPL")

# 실시간 주가를 다시 불러오기 위한 새로고침 버튼
if st.button("🔄 실시간 데이터 불러오기 / 새로고침"):
    if ticker_input:
        with st.spinner('실시간 데이터를 가져오는 중입니다...'):
            try:
                # 야후 파이낸스에서 데이터 호출
                stock = yf.Ticker(ticker_input.strip().upper())
                info = stock.info
                
                # 데이터 추출 (현재가, EPS, BPS)
                price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
                eps = info.get('trailingEps')
                bps = info.get('bookValue')
                name = info.get('longName', ticker_input.upper())
                
                if price and eps and bps:
                    # PER, PBR 계산
                    per = price / eps if eps > 0 else None
                    pbr = price / bps if bps > 0 else None
                    
                    st.subheader(f"🏢 {name}")
                    
                    # 3가지 주요 데이터 나란히 표시
                    col1, col2, col3 = st.columns(3)
                    col1.metric("실시간 주가", f"{price:,.2f}")
                    col2.metric("직전 EPS (주당순이익)", f"{eps:,.2f}")
                    col3.metric("직전 BPS (주당순자산)", f"{bps:,.2f}")
                    
                    st.divider()
                    
                    # 가치 평가 결과 표시
                    st.markdown("### 🔍 가치 평가 결과")
                    col4, col5 = st.columns(2)
                    
                    if per:
                        col4.metric("✅ PER (주가수익비율)", f"{per:.2f} 배")
                    else:
                        col4.metric("✅ PER", "계산 불가 (적자 기업)")
                        
                    if pbr:
                        col5.metric("✅ PBR (주가순자산비율)", f"{pbr:.2f} 배")
                    else:
                        col5.metric("✅ PBR", "계산 불가 (자본 잠식)")
                        
                else:
                    st.warning("⚠️ 야후 파이낸스에서 해당 종목의 재무 데이터를 완전히 제공하지 않습니다. 다른 종목을 시도해 주세요.")
                    
            except Exception as e:
                st.error("오류가 발생했습니다. 종목 코드가 정확한지 확인해 주세요.")
    else:
        st.warning("종목 코드를 입력해 주세요.")
