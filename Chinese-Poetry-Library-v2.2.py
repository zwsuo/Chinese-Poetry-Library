import streamlit as st
from datetime import datetime
import pymysql
from zhconv import convert
from contextlib import contextmanager
import traceback

# 页面配置
st.set_page_config(
    page_title="中国古诗词大全",
    page_icon="📓",
    layout="centered",
    initial_sidebar_state="auto"
)

# 页面标题
st.header("📓 :blue[诗词大全]", divider=True)

# GitHub链接
st.markdown(
    f'<a href="https://github.com/zwsuo/Chinese-Poetry-Library" target="_blank" style="float: right; margin-top: -60px;">'
    f'<img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="32" height="32" alt="GitHub">'
    f'</a>',
    unsafe_allow_html=True
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 字体定义 */
    @font-face {
        font-family: 'ShiciFont';
        src:
            local('TW-Kai'),
            local('FZQiGXKJF'),
            local('SimKai'),
            local('KaiTi');
        font-weight: bold;
        font-style: normal;
    }

    /* 全局样式 */
    .stApp {
        padding-top: 1.5rem;
        /* background-color: #f8f5f0; */
    }

    /* 诗词内容展示容器 */
    .terminal {
        background-color: #211A1A;
        color: cyan;
        padding: 1.5rem;
        border-radius: 0.5rem;
        font-family: 'ShiciFont', serif;
        font-size: 18px;
        line-height: 2.4;
        white-space: pre-wrap;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    /* 标题样式 */
    h1, h2, h3, h4 {
        font-family: 'ShiciFont', serif;
        color: #0A083C;
    }
    
    /* 输入框样式 */
    .stTextInput > div > div > input {
        border-radius: 0.3rem;
        border: 1px solid #d0c8b5;
        background-color: #fffcf5;
    }
    
    /* 信息框样式 */
    .stAlert {
        border-radius: 0.3rem;
    }
    
    /* 分割线样式 */
    hr {
        border-color: #d0c8b5;
        margin: 1.5rem 0;
    }
    
    /* 引用样式 */
    blockquote {
        border-left: 3px solid #5c4033;
        padding-left: 1rem;
        color: #052B17;
        background-color: #f0ebe0;
        border-radius: 0.3rem;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 显示当前时间
NOW_TIME = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
st.write("刷新时间： ", str(NOW_TIME))

# 数据库连接配置
DB_CONFIG = {
    'host': '192.168.5.111',
    'port': 3306,
    'user': 'root',
    'passwd': 'xxxxxxxx',
    'db': 'ChinesePoetry',
    'charset': 'utf8mb4'
}

@contextmanager
def get_db_connection():
    """创建数据库连接的上下文管理器"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        try:
            yield conn
        finally:
            conn.close()
    except pymysql.Error as e:
        st.error(f"数据库连接错误: {str(e)}")
        raise

def execute_query(sql, params=None):
    """执行SQL查询并返回结果"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
    except pymysql.Error as e:
        st.error(f"数据库查询错误: {str(e)}")
        st.info(f"SQL: {sql}")
        if params:
            st.info(f"参数: {params}")
        return []
    except Exception as e:
        st.error(f"执行查询时发生未知错误: {str(e)}")
        return []

def format_text(text):
    """格式化文本内容，替换分隔符为换行符"""
    if text:
        return text.replace('|', '\n')
    return ""

def display_poetry_content(title, author=None, content=None, yunlv=None, chapter=None, section=None):
    """统一展示诗词内容"""
    # 标题和作者/章节信息
    header_parts = []
    if title:
        header_parts.append(f"题目: {title}")
    if author:
        header_parts.append(f"作者: {author}")
    if chapter:
        header_parts.append(f"集合: {chapter}")
    if section:
        header_parts.append(f"篇章: {section}")
    
    st.markdown(f">#### {' | '.join(header_parts)}")
    
    # 正文内容
    if content:
        st.markdown("#### 正文:")
        st.markdown(f'<div class="terminal">{content}</div>', unsafe_allow_html=True)
    
    # 韵律信息（如果有）
    if yunlv:
        st.markdown("#### 韵律:")
        st.markdown(f'<div class="terminal">{yunlv}</div>', unsafe_allow_html=True)
    
    st.markdown("---")

def display_author_info(author_info):
    """展示作者信息"""
    if not author_info:
        return
    
    for author in author_info:
        name = author[0]
        intro = author[1]
        
        if name:
            st.info(f"#### 作者: {name}")
            
            if intro and len(str(intro).strip()) > 0:
                # 处理宋词作者简介前的破折号
                if isinstance(intro, str) and intro.startswith('--'):
                    intro = intro.lstrip('--')
                st.markdown(f">{intro}")
            else:
                st.markdown(">无简介!")

def build_search_query(table, author=None, title=None, keyword=None, chapter=None, section=None):
    """构建搜索查询（支持简繁混合搜索）"""
    conditions = []
    params = []
    
    # 简体搜索条件（保持原样）
    if author:
        conditions.append("(author LIKE %s OR author LIKE %s)")
        params.extend([f"%{author}%", f"%{convert(author, 'zh-hant')}%"])
    
    if title:
        conditions.append("(title LIKE %s OR title LIKE %s)")
        params.extend([f"%{title}%", f"%{convert(title, 'zh-hant')}%"])
    
    if keyword:
        conditions.append("(content LIKE %s OR content LIKE %s)")
        params.extend([f"%{keyword}%", f"%{convert(keyword, 'zh-hant')}%"])
    
    if chapter:
        conditions.append("(chapter LIKE %s OR chapter LIKE %s)")
        params.extend([f"%{chapter}%", f"%{convert(chapter, 'zh-hant')}%"])
    
    if section:
        conditions.append("(section LIKE %s OR section LIKE %s)")
        params.extend([f"%{section}%", f"%{convert(section, 'zh-hant')}%"])
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    # 没有查询条件时限制10条，有查询条件时显示全量结果
    limit_clause = " LIMIT 10" if not any([author, title, keyword, chapter, section]) else ""
    sql = f"SELECT * FROM {table} WHERE {where_clause}{limit_clause}"
    
    return sql, params

def get_author_info(table, author=None, title=None, keyword=None):
    """获取作者信息"""
    if not any([author, title, keyword]):
        return []
    
    conditions = []
    params = []
    
    # 根据不同条件构建查询
    if author:
        conditions.append("(p.author LIKE %s OR p.author LIKE %s)")
        params.extend([f"%{author}%", f"%{convert(author, 'zh-hant')}%"])
        join_field = "p.author_id = a.id"
    elif title and keyword:
        conditions.append("(p.title LIKE %s OR p.title LIKE %s)")
        conditions.append("(p.content LIKE %s OR p.content LIKE %s)")
        params.extend([f"%{title}%", f"%{convert(title, 'zh-hant')}%", 
                      f"%{keyword}%", f"%{convert(keyword, 'zh-hant')}%"])
        join_field = "p.author_id = a.id"
    elif title:
        conditions.append("(p.title LIKE %s OR p.title LIKE %s)")
        params.extend([f"%{title}%", f"%{convert(title, 'zh-hant')}%"])
        join_field = "p.author_id = a.id"
    elif keyword:
        conditions.append("(p.content LIKE %s OR p.content LIKE %s)")
        params.extend([f"%{keyword}%", f"%{convert(keyword, 'zh-hant')}%"])
        join_field = "p.author_id = a.id"
    else:
        return []
    
    # 确定作者简介字段名和正确的表名
    if table == "ChinesePoetry.poems":
        intro_field = "intro_l"
        author_table = "ChinesePoetry.poems_author"
    else:
        intro_field = "intro"
        author_table = "ChinesePoetry.poetry_author"
    
    where_clause = " AND ".join(conditions)
    sql = f"""
    SELECT DISTINCT name, {intro_field} 
    FROM {table} AS p 
    LEFT JOIN {author_table} AS a ON {join_field} 
    WHERE {where_clause}
    """
    
    try:
        return execute_query(sql, params)
    except Exception as e:
        st.warning(f"获取作者信息时出错: {str(e)}")
        return []

def search_poetry(poetry_type):
    """根据诗词类型执行相应的搜索功能"""
    if poetry_type == '唐诗':
        search_tang_song_poetry()
    elif poetry_type == '宋词':
        search_song_ci()
    elif poetry_type == '诗经':
        search_shi_jing()
    elif poetry_type == '论语':
        search_lun_yu()
    else:
        st.info("目前只有唐诗、宋词、诗经、论语，其他功能开发中...")

def search_tang_song_poetry():
    """搜索唐诗宋诗"""
    poetry_table = 'ChinesePoetry.poetry'
    
    # 输入框
    col1, col2 = st.columns(2)
    with col1:
        author = st.text_input('输入诗词作者:', key='tang_author').replace(' ', '')
    with col2:
        title = st.text_input('输入唐诗题目:', key='tang_title').replace(' ', '')
    
    keyword = st.text_input('输入关键词:', '明月松间照', key='tang_keyword').replace(' ', '')
    
    # 显示搜索条件
    search_info = f"检索内容: {author} {title} {keyword}"
    if any([author, title, keyword]):
        st.info(f"{search_info}")
    else:
        st.warning("请输入查询条件!（未输入条件只显示10条展示数据）")
    
    # 构建并执行查询
    sql, params = build_search_query(poetry_table, author, title, keyword)
    results = execute_query(sql, params)
    
    # 获取并显示作者信息
    author_info = get_author_info(poetry_table, author, title, keyword)
    display_author_info(author_info)
    
    # 显示查询结果
    if results:
        result_count = len(results)
        if any([author, title, keyword]) and result_count == 10:
            st.warning("查询结果数量大于10条，请输入更准确信息!")
        else:
            st.success(f"共检索到 {result_count} 条结果!")
        
        for result in results:
            title = result[2]
            content = format_text(result[3])
            yunlv = format_text(result[4])
            author = result[5]
            display_poetry_content(title, author, content, yunlv)
    else:
        st.error("### 没查到数据，你肯定是记错了!")

def search_song_ci():
    """搜索宋词"""
    poetry_table = 'ChinesePoetry.poems'
    
    # 输入框
    col1, col2 = st.columns(2)
    with col1:
        author = st.text_input('输入诗词作者:', key='ci_author')
        author = author.replace(' ', '') if author else ''
    with col2:
        title = st.text_input('输入词牌名: ', key='ci_title').replace(' ', '')
    keyword = st.text_input('输入关键词:', '一蓑烟雨任平生', key='ci_keyword').replace(' ', '')
    
    # 显示搜索条件
    search_info = f"检索内容: {author} {title} {keyword}"
    if any([author, title, keyword]):
        st.info(f"{search_info}")
    else:
        st.warning("请输入查询条件!（未输入条件只显示10条展示数据）")
    
    # 构建并执行查询
    sql, params = build_search_query(poetry_table, author, title, keyword)
    results = execute_query(sql, params)
    
    # 获取并显示作者信息
    author_info = get_author_info(poetry_table, author, title, keyword)
    display_author_info(author_info)
    
    # 显示查询结果
    if results:
        result_count = len(results)
        if result_count == 10:
            st.warning("查询结果数量大于10条，请输入更准确信息!")
        else:
            st.success(f"共检索到 {result_count} 条结果!")
        
        for result in results:
            title = result[2]
            content = format_text(result[3])
            author = result[4]
            display_poetry_content(title, author, content)
    else:
        st.error("### 没查到数据，你肯定是记错了!")

def search_shi_jing():
    """搜索诗经"""
    poetry_table = 'ChinesePoetry.shijing'
    
    # 输入框
    col1, col2, col3 = st.columns(3)
    with col1:
        title = st.text_input('输入题目:', key='shijing_title')
        title = title.replace(' ', '') if title else ''
    with col2:
        chapter = st.text_input('输入集合(风/雅/颂):', key='shijing_chapter').replace(' ', '')
    with col3:
        section = st.text_input('输入篇章:', key='shijing_section').replace(' ', '')
    
    keyword = st.text_input('输入关键词:', '俟我于城隅', key='shijing_keyword').replace(' ', '')
    
    # 显示搜索条件
    search_info = f"{title} {chapter} {section} {keyword}"
    if search_info.replace(' ', ''):
        st.info(f"检索内容： {search_info}")
    else:
        st.warning("当前未输入检索关键字，显示10条《诗经》展示数据！")
    
    # 构建并执行查询
    sql, params = build_search_query(poetry_table, None, title, keyword, chapter, section)
    results = execute_query(sql, params)
    
    # 显示查询结果
    if results:
        st.success(f"#### 查询到 {len(results)} 条结果")
        
        for result in results:
            title = result[1]
            chapter = result[2]
            section = result[3]
            content = format_text(result[4])
            display_poetry_content(title, None, content, None, chapter, section)
    else:
        st.error("### 没查到数据，你肯定是记错了！")

def search_lun_yu():
    """搜索论语"""
    poetry_table = 'ChinesePoetry.lunyu'
    
    # 输入框
    col1, col2 = st.columns(2)
    with col1:
        chapter = st.text_input('输入篇章:', key='lunyu_chapter').replace(' ', '')
    with col2:
        keyword = st.text_input('输入关键词:', '学而时习之', key='lunyu_keyword').replace(' ', '')
    
    # 显示搜索条件
    search_info = f"{chapter} {keyword}"
    if search_info.replace(' ', ''):
        st.info(f"检索内容： {search_info}")
    else:
        st.warning("当前未输入检索关键字，显示10条《论语》展示数据！")
    
    # 构建并执行查询
    sql, params = build_search_query(poetry_table, None, None, keyword, chapter)
    results = execute_query(sql, params)
    
    # 显示查询结果
    if results:
        st.success(f"#### 查询到 {len(results)} 条结果")
        
        for result in results:
            chapter = result[1]
            # 增强论语文本格式化
            content = result[2].replace('|', '\n').replace('"', '"\n').replace('。', '。\n')
            
            st.markdown(f"### 篇章: {chapter}")
            st.markdown("#### 正文:")
            st.markdown(f'<div class="terminal">{content}</div>', unsafe_allow_html=True)
    else:
        st.error("### 没查到数据，你肯定是记错了！")

if __name__ == '__main__':
    # 使用图标美化选择器
    st.markdown("### 🔍 选择查询类型")
    poetry_type = st.radio(
        '请选择诗词类型',
        ('唐诗', '宋词', '诗经', '论语', '其他'),
        horizontal=True,
        index=0
    )
    
    # 添加分隔线
    st.markdown("---")
    
    try:
        # 检查必要的依赖
        try:
            import pymysql
            import zhconv
        except ImportError as e:
            st.error(f"缺少必要的依赖包: {str(e)}")
            st.info("请运行: pip install pymysql zhconv")
            st.stop()
            
        search_poetry(poetry_type)
    except pymysql.Error as e:
        st.error(f"数据库连接错误: {str(e)}")
        st.info("请检查数据库配置和网络连接")
    except Exception as e:
        st.error(f"程序执行错误: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        st.info("请检查输入内容或联系开发者")
    st.caption('<p style="text-align: center;" > © zwsuo </p>', unsafe_allow_html=True)
