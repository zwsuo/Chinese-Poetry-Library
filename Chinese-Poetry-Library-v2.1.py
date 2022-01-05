
import streamlit as st
from datetime import datetime
import pymysql
from zhconv import convert

st.markdown("# 中国古诗词大全")

# 日期输入框
NOW_TIME = datetime.now()
st.write(NOW_TIME)

#连接数据库
db = pymysql.connect(
    host='192.168.xx.xx',
    port=3306,
    user='xxxxx',
    passwd='xxxxxxxx',
    db='ChinesePoetry',
    charset='utf8mb4'
)
cursor=db.cursor()

def tangsongshi():
    poetry_table = 'ChinesePoetry.poetry'
    Q_AUHTOR = st.text_input('输入诗词作者: ')
    Q_AUHTOR = convert(Q_AUHTOR, 'zh-hant').replace(' ','')
    Q_TITLE = st.text_input('输入唐诗题目: ')
    Q_TITLE = convert(Q_TITLE, 'zh-hant').replace(' ','')
    Q_KEYWORD = st.text_input('输入关键词: ','明月松间照')
    Q_KEYWORD = convert(Q_KEYWORD, 'zh-hant').replace(' ','')
    Q_ALL = "检索内容: "+"  "+str(Q_AUHTOR)+"  "+str(Q_TITLE)+"  "+(Q_KEYWORD)+"「结果大于10条时最多只展示10条!」"
    st.info(Q_ALL)
    SQL="SELECT * FROM {} where 1=1 ".format(poetry_table)
    if Q_AUHTOR and Q_TITLE and Q_KEYWORD:
        SQL = SQL + "AND author like '%{}%' AND title like '%{}%' AND content like '%{}%' limit 10".format(Q_AUHTOR,Q_TITLE,Q_KEYWORD)
        sql_author = "SELECT distinct name,intro FROM {} as p left join {}_author as a on p.author_id = a.id where p.author like '%{}%' ;".format(poetry_table,poetry_table,Q_AUHTOR)
        cursor.execute(sql_author)
        results_author = cursor.fetchall()
    elif  Q_AUHTOR and Q_TITLE and not Q_KEYWORD:
        SQL = SQL + "AND author like '%{}%' AND title like '%{}%' limit 10 ".format(Q_AUHTOR,Q_TITLE)
        sql_author = "SELECT distinct name,intro FROM {} as p left join {}_author as a on p.author_id = a.id where p.author like '%{}%' ;".format(poetry_table,poetry_table,Q_AUHTOR)
        cursor.execute(sql_author)
        results_author = cursor.fetchall()
    elif  Q_AUHTOR and not Q_TITLE and Q_KEYWORD:
        SQL = SQL + "AND author like '%{}%' AND content like '%{}%' limit 10 ".format(Q_AUHTOR,Q_KEYWORD)
        sql_author = "SELECT distinct name,intro FROM {} as p left join {}_author as a on p.author_id = a.id where p.author like '%{}%' ;".format(poetry_table,poetry_table,Q_AUHTOR)
        cursor.execute(sql_author)
        results_author = cursor.fetchall()
    elif not Q_AUHTOR and Q_TITLE and Q_KEYWORD:
        SQL = SQL + "AND title like '%{}%' AND content like '%{}%' limit 10 ".format(Q_TITLE,Q_KEYWORD)
        sql_author = "SELECT distinct name,intro FROM {} as p left join {}_author as a on p.author_id = a.id where p.content like '%{}%' and p.title like '%{}%';".format(poetry_table,poetry_table,Q_KEYWORD,Q_TITLE)
        cursor.execute(sql_author)
        results_author = cursor.fetchall()
    elif Q_AUHTOR and not Q_TITLE and not Q_KEYWORD:
        SQL = SQL + "AND author like '%{}%' limit 10 ".format(Q_AUHTOR)
        sql_author = "SELECT distinct name,intro FROM {} as p left join {}_author as a on p.author_id = a.id where p.author like '%{}%' ;".format(poetry_table,poetry_table,Q_AUHTOR)
        cursor.execute(sql_author)
        results_author = cursor.fetchall()
    elif not Q_AUHTOR and Q_TITLE and not Q_KEYWORD:
        SQL = SQL + "AND title like '%{}%' limit 10 ".format(Q_TITLE)
        sql_author = "SELECT distinct name,intro FROM {} as p left join {}_author as a on p.author_id = a.id where p.title like '%{}%' ;".format(poetry_table,poetry_table,Q_TITLE)
        cursor.execute(sql_author)
        results_author = cursor.fetchall()
    elif not Q_AUHTOR and not Q_TITLE and Q_KEYWORD:
        SQL = SQL + "AND content like '%{}%' limit 10 ".format(Q_KEYWORD)
        sql_author = "SELECT distinct name,intro FROM {} as p left join {}_author as a on p.author_id = a.id where p.content like '%{}%' ;".format(poetry_table,poetry_table,Q_KEYWORD)
        cursor.execute(sql_author)
        results_author = cursor.fetchall()
    else:
        SQL = SQL + " limit 10;"
        st.warning("请输入查询条件!（未输入条件只显示10条展示数据）")
        sql_author = ''
        results_author = ''

    cursor.execute(SQL)
    RESULTS = cursor.fetchall()

    if sql_author != '':
        cursor.execute(sql_author)
        results_author = cursor.fetchall()
        for r_a in results_author:
            result_author_name = r_a[0]
            result_author_intro = r_a[1]
            if len(result_author_intro) != 0:
                st.info("#### 作者: {} ".format(result_author_name))
                st.markdown(">{}".format(result_author_intro))
            else:
                st.info("#### 作者: {}".format(result_author_name))
                st.markdown(">无简介!")
    else:
        pass

    if len(RESULTS) != 0:
        RESULT_COUNT = len(RESULTS)
        if RESULT_COUNT == 10:
            st.warning("查询结果数量大于10条，请输入更准确信息!".format(RESULT_COUNT))
        else:
            st.success("共检索到 {} 条结果!".format(RESULT_COUNT))
        for i in RESULTS:
            i_title = i[2]
            i_content = i[3].replace('|','\n')
            i_yunlv = i[4].replace('|','\n')
            i_author = i[5]
            st.markdown("### 题目:{} | 作者:{}".format(i_title,i_author))
            st.markdown("#### 正文:")
            st.markdown("```\n{}\n```".format(i_content))
            st.markdown("#### 韵律:")
            st.markdown("```\n{}\n```".format(i_yunlv))
            st.markdown("---")
    else:
        st.error("### 没查到数据，你肯定是记错了!")


def songci():
    poetry_table = 'ChinesePoetry.poems'
    Q_AUHTOR = st.text_input('输入诗词作者: ').replace(' ','')
    Q_TITLE = st.text_input('输入词牌名: （宋词题目为后人所加，所以关键词不包含宋词题目，只有词牌名）').replace(' ','')
    Q_KEYWORD = st.text_input('输入关键词:','一蓑烟雨任平生').replace(' ','')
    Q_ALL = "检索内容: "+"  "+str(Q_AUHTOR)+"  "+str(Q_TITLE)+"  "+(Q_KEYWORD)+"「结果大于10条时最多只展示10条!」"
    st.info(Q_ALL)
    SQL="SELECT * FROM {} where 1=1 ".format(poetry_table)
    if Q_AUHTOR and Q_TITLE and Q_KEYWORD:
        SQL = SQL + "AND author like '%{}%' AND title like '%{}%' AND content like '%{}%' limit 10".format(Q_AUHTOR,Q_TITLE,Q_KEYWORD)
        sql_author = "SELECT distinct name,intro_l FROM {} as p left join {}_author as a on p.author_id = a.id where p.author like '%{}%' ;".format(poetry_table,poetry_table,Q_AUHTOR)
        cursor.execute(sql_author)
        results_author = cursor.fetchall()
    elif  Q_AUHTOR and Q_TITLE and not Q_KEYWORD:
        SQL = SQL + "AND author like '%{}%' AND title like '%{}%' limit 10 ".format(Q_AUHTOR,Q_TITLE)
        sql_author = "SELECT distinct name,intro_l FROM {} as p left join {}_author as a on p.author_id = a.id where p.author like '%{}%' ;".format(poetry_table,poetry_table,Q_AUHTOR)
        cursor.execute(sql_author)
        results_author = cursor.fetchall()
    elif  Q_AUHTOR and not Q_TITLE and Q_KEYWORD:
        SQL = SQL + "AND author like '%{}%' AND content like '%{}%' limit 10 ".format(Q_AUHTOR,Q_KEYWORD)
        sql_author = "SELECT distinct name,intro_l FROM {} as p left join {}_author as a on p.author_id = a.id where p.author like '%{}%' ;".format(poetry_table,poetry_table,Q_AUHTOR)
        cursor.execute(sql_author)
        results_author = cursor.fetchall()
    elif not Q_AUHTOR and Q_TITLE and Q_KEYWORD:
        SQL = SQL + "AND title like '%{}%' AND content like '%{}%' limit 10 ".format(Q_TITLE,Q_KEYWORD)
        sql_author = "SELECT distinct name,intro_l FROM {} as p left join {}_author as a on p.author_id = a.id where p.content like '%{}%' and p.title like '%{}%';".format(poetry_table,poetry_table,Q_KEYWORD,Q_TITLE)
        cursor.execute(sql_author)
        results_author = cursor.fetchall()
    elif Q_AUHTOR and not Q_TITLE and not Q_KEYWORD:
        SQL = SQL + "AND author like '%{}%' limit 10 ".format(Q_AUHTOR)
        sql_author = "SELECT distinct name,intro_l FROM {} as p left join {}_author as a on p.author_id = a.id where p.author like '%{}%' ;".format(poetry_table,poetry_table,Q_AUHTOR)
        cursor.execute(sql_author)
        results_author = cursor.fetchall()
    elif not Q_AUHTOR and Q_TITLE and not Q_KEYWORD:
        SQL = SQL + "AND title like '%{}%' limit 10 ".format(Q_TITLE)
        sql_author = "SELECT distinct name,intro_l FROM {} as p left join {}_author as a on p.author_id = a.id where p.title like '%{}%' ;".format(poetry_table,poetry_table,Q_TITLE)
        cursor.execute(sql_author)
        results_author = cursor.fetchall()
    elif not Q_AUHTOR and not Q_TITLE and Q_KEYWORD:
        SQL = SQL + "AND content like '%{}%' limit 10 ".format(Q_KEYWORD)
        sql_author = "SELECT distinct name,intro_l FROM {} as p left join {}_author as a on p.author_id = a.id where p.content like '%{}%' ;".format(poetry_table,poetry_table,Q_KEYWORD)
        cursor.execute(sql_author)
        results_author = cursor.fetchall()
    else:
        SQL = SQL + " limit 10;"
        st.warning("请输入查询条件!（未输入条件只显示10条展示数据）")
        sql_author = ''
        results_author = ''

    cursor.execute(SQL)
    RESULTS = cursor.fetchall()

    if sql_author != '':
        cursor.execute(sql_author)
        results_author = cursor.fetchall()
        for r_a in results_author:
            result_author_name = r_a[0]
            result_author_intro_l = r_a[1]
            if result_author_intro_l is not None:
                result_author_intro_l = result_author_intro_l.lstrip('--')
                if len(result_author_intro_l) != 0:
                    st.info("#### 作者: {} ".format(result_author_name))
                    st.markdown(">{}".format(result_author_intro_l))
                else:
                    pass
            else:
                pass
    else:
        pass

    if len(RESULTS) != 0:
        RESULT_COUNT = len(RESULTS)
        if RESULT_COUNT == 10:
            st.warning("查询结果数量大于10条，请输入更准确信息!".format(RESULT_COUNT))
        else:
            st.success("共检索到 {} 条结果!".format(RESULT_COUNT))
        for i in RESULTS:
            i_title = i[2]
            i_content = i[3].replace('|','\n')
            i_author = i[4]
            st.markdown("### 题目:{} | 作者:{}".format(i_title,i_author))
            st.markdown("#### 正文:")
            st.markdown("```\n{}\n```".format(i_content))
            st.markdown("---")
    else:
        st.error("### 没查到数据，你肯定是记错了!")


def shijing():
    poetry_table = 'ChinesePoetry.shijing'
    Q_TITLE = st.text_input('输入题目: ').replace(' ','')
    Q_CHAPTER = st.text_input('输入集合(风/雅/颂): ').replace(' ','')
    Q_SECTION = st.text_input('输入篇章: ').replace(' ','')
    Q_KEYWORD = st.text_input('输入关键词:','俟我于城隅').replace(' ','')
    Q_ALL = str(Q_TITLE)+"  "+str(Q_CHAPTER)+"  "+str(Q_SECTION)+" "+str(Q_KEYWORD)
    if len(Q_ALL.replace(' ','')) != 0:
        st.info("检索内容： "+Q_ALL)
    else:
        st.warning("当前未输入检索关键字，显示《诗经》全集！")
    SQL="SELECT * FROM {} where title like '%{}%' and chapter like '%{}%' and section like '%{}%' and content like '%{}%';".format(poetry_table,Q_TITLE,Q_CHAPTER,Q_SECTION,Q_KEYWORD)
    cursor.execute(SQL)
    RESULTS = cursor.fetchall()

    if RESULTS == ():
        st.error("### 没查到数据，你肯定是记错了！")
    else:
        st.success("#### 查询到 {} 条结果".format(len(RESULTS)))
    for i in RESULTS:
        i_title = i[1]
        i_chapter = i[2]
        i_section = i[3]
        i_content = i[4].replace('|','\n')
        st.markdown("### 题目:{} | 集合:{} | 篇章:{} ".format(i_title,i_chapter,i_section))
        st.markdown("#### 正文:")
        st.markdown("```\n{}\n```".format(i_content))
    cursor.close();
    db.close();


def lunyu():
    poetry_table = 'ChinesePoetry.lunyu'
    Q_CHAPTER = convert(st.text_input('输入篇章: ').replace(' ',''),'zh-hant')
    Q_KEYWORD = convert(st.text_input('输入关键词:','学而时习之').replace(' ',''),'zh-hant')
    Q_ALL = str(Q_CHAPTER)+"  "+str(Q_KEYWORD)
    if len(Q_ALL.replace(' ','')) != 0:
        st.info("检索内容： "+Q_ALL)
    else:
        st.warning("当前未输入检索关键字，显示《论语》全集！")
    SQL="SELECT * FROM {} where chapter like '%{}%' and content like '%{}%';".format(poetry_table,Q_CHAPTER,Q_KEYWORD)
    cursor.execute(SQL)
    RESULTS = cursor.fetchall()

    if RESULTS == ():
        st.error("### 没查到数据，你肯定是记错了！")
    else:
        st.success("#### 查询到 {} 条结果".format(len(RESULTS)))
    for i in RESULTS:
        i_chapter = i[1]
        i_content = i[2].replace('|','\n').replace("”","”\n").replace("。","。\n")
        st.markdown("### 篇章:{} ".format(i_chapter))
        st.markdown("#### 正文:")
        st.markdown("{}".format(i_content))
    cursor.close();
    db.close();


if  __name__ == '__main__':
    poetry_type = st.radio('请选择诗词类型', ('其他','唐诗', '宋词', '诗经','论语'))
    if poetry_type == '唐诗':
        tangsongshi()
    if poetry_type == '宋词':
        songci()
    if poetry_type == '诗经':
        shijing()
    if poetry_type == '论语':
        lunyu()
    else:
        st.info("目前只有唐诗、宋词、诗经、论语，其他ToDo...")
