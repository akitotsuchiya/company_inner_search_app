"""
このファイルは、Webアプリのメイン処理が記述されたファイルです。
"""

############################################################
# 1. ライブラリの読み込み
############################################################
# 「.env」ファイルから環境変数を読み込むための関数
from dotenv import load_dotenv
# ログ出力を行うためのモジュール
import logging
# streamlitアプリの表示を担当するモジュール
import streamlit as st
# （自作）画面表示以外の様々な関数が定義されているモジュール
import utils
# （自作）アプリ起動時に実行される初期化処理が記述された関数
from initialize import initialize
# （自作）画面表示系の関数が定義されているモジュール
import components as cn
# （自作）変数（定数）がまとめて定義・管理されているモジュール
import constants as ct


############################################################
# 2. 設定関連
############################################################
# ブラウザタブの表示文言を設定
st.set_page_config(
    page_title=ct.APP_NAME,
    layout="wide"  # 画面幅いっぱいに表示
)

# ログ出力を行うためのロガーの設定
logger = logging.getLogger(ct.LOGGER_NAME)


############################################################
# 3. 初期化処理
############################################################
try:
    # 初期化処理（「initialize.py」の「initialize」関数を実行）
    initialize()
except Exception as e:
    # エラーログの出力
    logger.error(f"{ct.INITIALIZE_ERROR_MESSAGE}\n{e}")
    # エラーメッセージの画面表示
    st.error(utils.build_error_message(ct.INITIALIZE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    # 後続の処理を中断
    st.stop()

# アプリ起動時のログファイルへの出力
if not "initialized" in st.session_state:
    st.session_state.initialized = True
    logger.info(ct.APP_BOOT_MESSAGE)


############################################################
# 4. 初期表示
############################################################
# 問題３：画面修正 - 左ペインと右ペインのレイアウト作成
left_pane, right_pane = st.columns([1, 3])

with left_pane:
    # 左ペインの背景色設定
    st.markdown(
        """
        <style>
        .stColumn:first-child {
            background-color: #e9ecef;
            padding: 15px 20px;
            padding-top: 60px;
            border-radius: 10px;
            margin-right: 10px;
            min-height: calc(100vh - 8rem);
            position: fixed;
            width: 22%;
            top: 2rem;
            left: 2rem;
            bottom: 2rem;
            overflow-y: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    # モード表示（左ペインに配置）
    cn.display_select_mode()

with right_pane:
    # 右ペインの表示幅制限と中央揃え
    st.markdown(
        """
        <style>
        .stColumn:last-child {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-left: 2rem;
            padding-right: 2rem;
            margin-left: calc(22% + 3rem);
            position: relative;
            min-height: calc(100vh - 4rem);
        }
        .stColumn:last-child > div {
            max-width: 700px;
            width: 100%;
            margin-left: auto;
            margin-right: auto;
        }
        .stChatMessage {
            max-width: 650px;
            margin: 0;
            position: relative;
            text-align: left;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    # タイトル表示
    cn.display_app_title()

    # AIメッセージの初期表示
    cn.display_initial_ai_message()


############################################################
# 5. 会話ログの表示
############################################################
# 問題３：画面修正 - 会話ログを右ペインに配置
with right_pane:
    try:
        # 会話ログの表示
        cn.display_conversation_log()
    except Exception as e:
        # エラーログの出力
        logger.error(f"{ct.CONVERSATION_LOG_ERROR_MESSAGE}\n{e}")
        # エラーメッセージの画面表示
        st.error(utils.build_error_message(ct.CONVERSATION_LOG_ERROR_MESSAGE), icon=ct.ERROR_ICON)
        # 後続の処理を中断
        st.stop()


############################################################
# 6. チャット入力の受け付け
############################################################
# 問題３：画面修正 - チャット入力を右ペインに配置
with right_pane:
    # チャット入力エリアのスタイル設定
    st.markdown(
        """
        <style>
        .stChatInput {
            position: fixed;
            bottom: 2rem;
            left: calc(25% + 2rem);
            right: 2rem;
            max-width: 650px;
            margin-left: auto;
            margin-right: auto;
            z-index: 999;
            padding: 0.25rem 1rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stChatInput > div {
            max-width: 100%;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # チャット入力の前に適度な余白を追加
    st.markdown("<br>", unsafe_allow_html=True)
    
    # チャット入力ボックス
    chat_message = st.chat_input(ct.CHAT_INPUT_HELPER_TEXT)
    
    # チャット入力の後にも余白を追加（画面下にぴったりくっつかないように）
    st.markdown("<br><br>", unsafe_allow_html=True)


############################################################
# 7. チャット送信時の処理
############################################################
if chat_message:
    # 問題３：画面修正 - チャット送信時の処理を右ペインに配置
    with right_pane:
        # ==========================================
        # 7-1. ユーザーメッセージの表示
        # ==========================================
        # ユーザーメッセージのログ出力
        logger.info({"message": chat_message, "application_mode": st.session_state.mode})

        # ユーザーメッセージを表示
        with st.chat_message("user"):
            st.markdown(chat_message)

        # ==========================================
        # 7-2. LLMからの回答取得
        # ==========================================
        # 「st.spinner」でグルグル回っている間、表示の不具合が発生しないよう空のエリアを表示
        res_box = st.empty()
        # LLMによる回答生成（回答生成が完了するまでグルグル回す）
        with st.spinner(ct.SPINNER_TEXT):
            try:
                # 画面読み込み時に作成したRetrieverを使い、Chainを実行
                llm_response = utils.get_llm_response(chat_message)
            except Exception as e:
                # エラーログの出力
                logger.error(f"{ct.GET_LLM_RESPONSE_ERROR_MESSAGE}\n{e}")
                # エラーメッセージの画面表示
                st.error(utils.build_error_message(ct.GET_LLM_RESPONSE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
                # 後続の処理を中断
                st.stop()
        
        # ==========================================
        # 7-3. LLMからの回答表示
        # ==========================================
        with st.chat_message("assistant"):
            try:
                # ==========================================
                # モードが「社内文書検索」の場合
                # ==========================================
                if st.session_state.mode == ct.ANSWER_MODE_1:
                    # 入力内容と関連性が高い社内文書のありかを表示
                    content = cn.display_search_llm_response(llm_response)

                # ==========================================
                # モードが「社内問い合わせ」の場合
                # ==========================================
                elif st.session_state.mode == ct.ANSWER_MODE_2:
                    # 入力に対しての回答と、参照した文書のありかを表示
                    content = cn.display_contact_llm_response(llm_response)
                
                # AIメッセージのログ出力
                logger.info({"message": content, "application_mode": st.session_state.mode})
            except Exception as e:
                # エラーログの出力
                logger.error(f"{ct.DISP_ANSWER_ERROR_MESSAGE}\n{e}")
                # エラーメッセージの画面表示
                st.error(utils.build_error_message(ct.DISP_ANSWER_ERROR_MESSAGE), icon=ct.ERROR_ICON)
                # 後続の処理を中断
                st.stop()

        # ==========================================
        # 7-4. 会話ログへの追加
        # ==========================================
        # 表示用の会話ログにユーザーメッセージを追加
        st.session_state.messages.append({"role": "user", "content": chat_message})
        # 表示用の会話ログにAIメッセージを追加
        st.session_state.messages.append({"role": "assistant", "content": content})