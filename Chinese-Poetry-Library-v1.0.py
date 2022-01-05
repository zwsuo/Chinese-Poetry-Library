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

q_keyword = st.text_input('输入关键词（宋词题目为后人所加，所以关键词不包含宋词题目，只有词牌名）:','寇准')

poetry_type = st.radio('请选择诗词类型', ('其他','唐诗', '宋词', '诗经','论语'))
if poetry_type == '唐诗':
    poetry_table = 'poetry'
    q_keyword = convert(q_keyword, 'zh-hant')
    SQL="SELECT * FROM ChinesePoetry.{} where author like '%{}%' or title like '%{}%' or content like '%{}%'  limit 10;".format(poetry_table,q_keyword,q_keyword,q_keyword)
    cursor.execute(SQL)
    RESULT = cursor.fetchall()
    if RESULT == ():
        st.error("### 没查到数据，你肯定是记错了！")
    else:
        SQL_NUM="SELECT count(*) FROM ChinesePoetry.{} where author like '%{}%' or title like '%{}%' or content like '%{}%'  limit 10;".format(poetry_table,q_keyword,q_keyword,q_keyword)
        cursor.execute(SQL_NUM)
        RESULT_NUM = cursor.fetchall()[0][0]
        if RESULT_NUM > 10:
            st.success("#### 查询到 {} 条结果（只显示10条）".format(RESULT_NUM))
        else:
            st.success("#### 查询到 {} 条结果".format(RESULT_NUM))
        try:
            SQL_AUTHOR = "SELECT * FROM ChinesePoetry.poetry_author where name like '%{}%'".format(q_keyword)
            cursor.execute(SQL_AUTHOR)
            RESULT_AUTHOR = cursor.fetchall()[0][2]
            st.info("#### 人物介绍: ")
            st.markdown(">{}".format(RESULT_AUTHOR))
        except Exception as ee:
            st.info("查询的不是作者姓名！")
        for i in RESULT:
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
        cursor.close();
        db.close();

elif poetry_type == '宋词':
    poetry_table = 'poems'
    SQL="SELECT * FROM ChinesePoetry.{} where author like '%{}%' or title like '%{}%' or content like '%{}%' limit 10;".format(poetry_table,q_keyword,q_keyword,q_keyword)
    cursor.execute(SQL)
    RESULT = cursor.fetchall()
    if RESULT == ():
        st.error("### 没查到数据，你肯定是记错了！")
    else:
        SQL_NUM="SELECT count(*) FROM ChinesePoetry.{} where author like '%{}%' or title like '%{}%' or content like '%{}%' limit 10;".format(poetry_table,q_keyword,q_keyword,q_keyword)
        cursor.execute(SQL_NUM)
        RESULT_NUM = cursor.fetchall()[0][0]
        if RESULT_NUM > 10:
            st.success("#### 查询到 {} 条结果（只显示10条）".format(RESULT_NUM))
        else:
            st.success("#### 查询到 {} 条结果".format(RESULT_NUM))
        try:
            SQL_AUTHOR = "SELECT * FROM ChinesePoetry.poems_author where name like '%{}%'".format(q_keyword)
            cursor.execute(SQL_AUTHOR)
            RESULT_AUTHOR = cursor.fetchall()[0][2]
            st.info("#### 人物介绍: ")
            st.markdown(">{}".format(RESULT_AUTHOR))
        except Exception as ee:
            st.info("查询的不是作者姓名！")
        for i in RESULT:
            i_title = i[2]
            i_content = i[3].replace('|','\n')
            i_author = i[4]
            st.markdown("### 词牌:{} | 作者:{}".format(i_title,i_author))
            st.markdown("#### 正文:")
            st.markdown("```\n{}\n```".format(i_content))
            st.markdown("---")
        cursor.close();
        db.close();

elif poetry_type == '诗经':
    poetry_table = 'shijing'
    SQL="SELECT * FROM ChinesePoetry.{} where title like '%{}%' or chapter like '%{}%' or section like '%{}%  limit 10' or content like '%{}%';".format(poetry_table,q_keyword,q_keyword,q_keyword,q_keyword)
    cursor.execute(SQL)
    RESULT = cursor.fetchall()
    if RESULT == ():
        st.error("### 没查到数据，你肯定是记错了！")
    else:
        SQL_NUM="SELECT count(*) FROM ChinesePoetry.{} where title like '%{}%' or chapter like '%{}%' or section like '%{}%' or content like '%{}%' limit 10;".format(poetry_table,q_keyword,q_keyword,q_keyword,q_keyword)
        cursor.execute(SQL_NUM)
        RESULT_NUM = cursor.fetchall()[0][0]
        if RESULT_NUM > 10:
            st.success("#### 查询到 {} 条结果（只显示10条）".format(RESULT_NUM))
        else:
            st.success("#### 查询到 {} 条结果".format(RESULT_NUM))
        for i in RESULT:
            i_title = i[1]
            i_chapter = i[2]
            i_section = i[3]
            i_content = i[4].replace('|','\n')
            st.markdown("### 题目:{} | 风雅颂:{} | 风:{} ".format(i_title,i_chapter,i_section))
            st.markdown("#### 正文:")
            st.markdown("```\n{}\n```".format(i_content))
    cursor.close();
    db.close();

elif poetry_type == '论语':
    poetry_table = 'lunyu'
    q_keyword = convert(q_keyword, 'zh-hant')
    SQL="SELECT * FROM ChinesePoetry.{} where chapter like '%{}%' or content like '%{}%';".format(poetry_table,q_keyword,q_keyword)
    cursor.execute(SQL)
    RESULT = cursor.fetchall()
    if RESULT == ():
        st.error("### 没查到数据，你肯定是记错了！")
    else:
        SQL_NUM="SELECT count(*) FROM ChinesePoetry.{} where chapter like '%{}%' or content like '%{}%';".format(poetry_table,q_keyword,q_keyword)
        cursor.execute(SQL_NUM)
        RESULT_NUM = cursor.fetchall()[0][0]
        if RESULT_NUM > 10:
            st.success("#### 查询到 {} 条结果（只显示10条）".format(RESULT_NUM))
        else:
            st.success("#### 查询到 {} 条结果".format(RESULT_NUM))
        for i in RESULT:
            i_chapter = i[1]
            i_content = i[2].replace('|','\n')
            st.markdown("### 章节:{}".format(i_chapter))
            st.markdown("#### 正文:")
            st.markdown("```\n{}\n```".format(i_content))
        cursor.close();
        db.close();

else:
    st.info("目前只有唐诗、宋词、诗经、论语，其他ToDo...")