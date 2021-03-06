import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import streamlit as st
import base64
from nltk import Text
from nltk import FreqDist
from wordcloud import WordCloud

st.write("""
# WordCloud Generator
""")
expander_bar1 = st.expander("About", expanded=True)
expander_bar1.markdown("""
* NTIS의 한글 키워드 정보를 이용해 워드 클라우드를 그립니다.
* 입력 엑셀파일에 "한글키워드" 필드가 반드시 포함되어 있어야 합니다.
* 파일을 업로드하면 그래프와 wordcloud 메뉴들이 화면에 나타납니다.
* 사용방법

    * 첫째, 왼쪽 Side bar에서 단어갯수 지정
    * 둘째, 왼쪽 Side bar에서 제외할 단어 지정
    * 셋째, 메인에서 플롯으로 확인
    * 위의 순서를 반복하면서 단어 갯수와 제외할 단어 결정

* 옵션으로 유사한 단어들을 하나로 수정하는 것도 가능합니다. 
    * 단, 두개 이상의 단어를 수정할 경우, sidebar의 예와 같이 미세먼지를 첫번째로 놓고 초미세먼지를 두번째로 놓으면 알고리즘은 순차적으로 발생하기 때문에 초미세먼지를 완전히 걸러내지 못합니다. 이 경우에는 초미세먼지를 먼저 쓰고 두번째로 미세먼지를 써야 제대로 걸러집니다.
    * 여러개 단어를 수정하고 싶으면 엑셀에서 작업하는 것을 강력 추천합니다. 여기서는 간단한 단어만 변경.. 
""")

# mpl.rc('font', family='NanumGothic')
mpl.rcParams['font.size'] = 13
font_name = FontProperties(fname='.fonts/NanumGothic.ttf').get_name()
mpl.rc('font', family=font_name)

# 유니코드에서 음수 부호 설정
mpl.rc('axes', unicode_minus=False)
# 그래프 기본사이즈 설정
plt.rcParams["figure.figsize"] = (10,8)

### input features in the sidebar
st.sidebar.header('User Input Features')
# 0. 파일 열기
# Collects user input features into dataframe
uploaded_file = st.sidebar.file_uploader("Upload your excel file", type=["xlsx"])
try: 
    input_df = pd.read_excel(uploaded_file)
except:
    input_df = None
st.sidebar.write("""***""")

# 1. 순위 지정
st.sidebar.subheader('단어 갯수 설정')
rank = st.sidebar.slider('ex) 최다빈도 단어 1위부터 30위까지 보여주려면 30으로 지정', 10, 100, 30)
st.sidebar.write("""***""")

# 2. 카운팅 안할 단어 지정
st.sidebar.write("""### 제외할 단어 지정""")
stop_words = '및', '환경', '오염', '|', '및', '초', '성', '기술', '시스템', \
              '구조', '의', '중심으로', '관한', '대한', ':', '기반', '효과', \
              '개발', '에', '과', '연구', '적', '방법', '위한','변화', '미치는',\
              '활용', '-', '난', '프로', '미세먼지'

words = st.sidebar.text_area("제외할 단어를 따옴표로 감싸 아래와 같이 입력", stop_words, height=250)
st.sidebar.write("""***""")

st.sidebar.write('단어를 수정할 수 있습니다.')
input1 = st.sidebar.text_input('변경할 단어1', '미세먼지')
input2 = st.sidebar.text_input('새로운 단어1', 'DUST')
input3 = st.sidebar.text_input('변경할 단어2', '초미세먼지')
input4 = st.sidebar.text_input('새로운 단어2', 'DUST')
input5 = st.sidebar.text_input('변경할 단어3', '초초미세먼지')
input6 = st.sidebar.text_input('새로운 단어3', 'DUST')

# 3. 토큰 만들기
def str_keyword(df):
    string = ''
    for i in range(len(df)):
        try:
            string += df.iloc[i]['한글키워드'].replace('○ ', '').replace(input1, input2).replace(input3, input4)
        except:
            print(type(df.iloc[i]['한글키워드']))
    return string

@st.cache
def tokenizer(df, words):
    string = str_keyword(df)
    tokens = string.split(',')
    tokens = [tok.split(' ') for tok in tokens]  
    token_final = []
    for l in tokens:
        for item in l:
            if item != '':
                token_final.append(item)
    result = []
    for w in token_final:
        if w not in words:
            result.append(w)
    return result

if input_df is not None:
    tokens = tokenizer(input_df, words)
    #st.write(words)

# 4. 그래프 그리기
if input_df is not None:
    st.subheader('1. Display a plot')
    filename = 'ex1.png'
    figsize = (12, 6)
    expander_bar2 = st.expander("About")
    expander_bar2.markdown("""
        * 그래프에 표시된 단어들을 확인하면서 의미없는 단어는 제외해 주세요.""")
    if st.button('그래프 표시'):
        st.write('단어별 빈도수 (' + str(rank) + ' Rank 까지)' )
        f, ax = plt.subplots(figsize=figsize)
        common_words = Text(tokens)
        ax = common_words.plot(rank)
        plt.xlabel('빈도가 높은 단어')
        plt.xticks(fontsize =10)
        st.pyplot(f)
    st.sidebar.write("""***""")

# 가장 많이 사용된 단어 카운팅
@st.cache
def get_most_common_words(tokens, rank):
    fd_names = FreqDist(tokens)
    return fd_names.most_common(rank), fd_names
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    b64 = base64.b64encode(csv.encode(encoding='utf-8-sig')).decode(encoding='utf-8-sig')
    href = f'<a href="data:file/csv;base64,{b64}" download="common_words.csv">Download CSV File</a>'
    return href

if input_df is not None:
    # 5. Download dataframe
    st.subheader('2. Download a table') 
    most_words, fd_names = get_most_common_words(tokens, rank)
    most_df = pd.DataFrame(most_words, columns=['단어', '빈도'])
    st.dataframe(most_df.head(10))
    st.markdown(filedownload(most_df), unsafe_allow_html=True)
    st.write("""***""")

## 6. Display wordcloud
def draw_wordcloud(fd):
    wc = WordCloud(width=1000, height=600, background_color='white', font_path='.fonts/NanumGothic.ttf')
    plt.imshow(wc.generate_from_frequencies(fd))
    plt.axis('off')
    plt.show()

if input_df is not None:
    st.subheader('3. Create a wordcloud image')
    if st.button('워드클라우드 표시'):
        draw_wordcloud(fd_names)
        st.pyplot(plt)

    st.write("""
    ***
    """)


## 7. Display wordcloud
def draw_wordcloud(fd):
    wc = WordCloud(width=1000, height=600, background_color='white', font_path='.fonts/NanumGothic.ttf')
    plt.imshow(wc.generate_from_frequencies(fd))
    plt.axis('off')
    plt.show()



if input_df is not None:
    fd_names_upper = {}
    for i in range(rank):
        fd_names_upper[most_words[i][0]] = most_words[i][1]

    st.subheader('4. Top ranking image')
    if st.button('워드클라우드(상위랭크만) 표시'):
        draw_wordcloud(fd_names_upper)
        st.pyplot(plt)

    st.write("""
    ***
    """)

