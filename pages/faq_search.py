import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# 1. DB 연결 설정 (사용자 정보에 맞게 수정)
# 형식: mysql+pymysql://<ID>:<PASSWORD>@<HOST>:<PORT>/<DB_NAME>
db_config = "mysql+pymysql://root:root1234@localhost:3306/examplesdb"
engine = create_engine(db_config)

def run_query(query, params=None):
    """SQL 쿼리를 실행하고 결과를 데이터프레임으로 반환"""
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, params=params)

def main():
    st.set_page_config(page_title="FAQ DB Explorer", layout="wide")
    st.title("🗂️ FAQ 데이터베이스 통합 검색 시스템")

    # 사이드바: 다양한 검색 조건 (SELECT의 WHERE/ORDER BY 절 구성)
    st.header("🔍 검색 및 필터 설정")

    # (1) 브랜드 필터 (brand_code)
    brand_list = ["전체", "HYUNDAI", "KIA", "GENESIS"]
    selected_brand = st.selectbox("브랜드 선택", brand_list)

    # (2) 카테고리 필터 (DB에서 실시간 select)
    cat_query = "SELECT DISTINCT category FROM FAQ"
    categories = ["전체"] + run_query(cat_query)['category'].tolist()
    selected_category = st.selectbox("카테고리 선택", categories)

    # (3) 키워드 검색 (Question, Answer 대상)
    search_keyword = st.text_input("검색어 입력 (질문/답변)")

    # (4) 정렬 기준 (ORDER BY)
    sort_option = st.radio("정렬 기준", ["최신순", "오래된순", "제목순"])

    # ---------------------------------------------------------
    # 3. 동적 SELECT 쿼리 생성
    # ---------------------------------------------------------
    base_query = "SELECT * FROM FAQ WHERE 1=1"
    params = {}

    # 브랜드 필터 추가
    if selected_brand != "전체":
        base_query += " AND brand_code = :brand"
        params['brand'] = selected_brand

    # 카테고리 필터 추가
    if selected_category != "전체":
        base_query += " AND category = :category"
        params['category'] = selected_category

    # 키워드 검색 추가 (LIKE 처리)
    if search_keyword:
        base_query += " AND (question LIKE :keyword OR answer LIKE :keyword)"
        params['keyword'] = f"%{search_keyword}%"

    # 정렬 조건 추가
    if sort_option == "최신순":
        base_query += " ORDER BY created_at DESC"
    elif sort_option == "오래된순":
        base_query += " ORDER BY created_at ASC"
    else:
        base_query += " ORDER BY question ASC"
    
    # 쿼리 실행
    try:
        results = run_query(base_query, params)
        
        # UI 출력
        st.subheader(f"📌 검색 결과 ({len(results)}건)")
        
        if not results.empty:
            # 1. 데이터프레임 출력 (인터랙티브 표)
            st.dataframe(
                results,
                use_container_width=True, # 화면 너비에 맞게 확장
                column_config={           # 컬럼 설정 (이름 변경 및 링크 등)
                    "faq_id": "🆔 ID",
                    "brand_code": "브랜드",
                    "category": "카테고리",
                    "question": "질문 내용",
                    "answer": "답변 내용",
                    "updated_at": st.column_config.DatetimeColumn("마지막 수정일", format="YYYY-MM-DD HH:mm")
                },
                hide_index=True # 왼쪽 인덱스 번호 숨기기
            )
            
            # 2. (선택 사항) 만약 답변 내용이 너무 길어 표에서 보기 힘들다면 
            # 특정 행을 선택했을 때 아래에 상세 내용을 띄워주는 기능을 추가할 수 있습니다.
            
        else:
            st.info("조건에 맞는 데이터가 없습니다.")

    except Exception as e:
        st.error(f"DB 연결 또는 쿼리 오류: {e}")
    # # 쿼리 실행
    # try:
    #     results = run_query(base_query, params)
        
    #     # UI 출력
    #     st.subheader(f"📌 검색 결과 ({len(results)}건)")
        
    #     if not results.empty:
    #         for _, row in results.iterrows():
    #             with st.container():
    #                 # 카드 형태의 디자인
    #                 col1, col2 = st.columns([1, 4])
    #                 with col1:
    #                     st.caption(f"🆔 ID: {row['faq_id']}")
    #                     st.markdown(f"**`{row['brand_code']}`**")
    #                     st.markdown(f"`{row['category']}`")
    #                 with col2:
    #                     with st.expander(f"❓ {row['question']}", expanded=False):
    #                         st.write("**답변 내용:**")
    #                         st.info(row['answer'])
    #                         st.caption(f"마지막 수정일: {row['updated_at']}")
    #                 st.divider()
    #     else:
    #         st.info("조건에 맞는 데이터가 없습니다.")

    # except Exception as e:
    #     st.error(f"DB 연결 또는 쿼리 오류: {e}")

if __name__ == "__main__":
    main()