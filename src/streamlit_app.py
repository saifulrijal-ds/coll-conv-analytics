import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from .analyzer import SimpleCollectionAnalyzer

# Load environment variables
load_dotenv()

def read_file_content(file_content):
    """Try different encodings to read the file content"""
    encodings = ['utf-8', 'cp1252', 'iso-8859-1', 'latin1']
    
    for encoding in encodings:
        try:
            return file_content.decode(encoding)
        except UnicodeDecodeError:
            continue
    
    # If no encoding works, try reading byte by byte
    try:
        return file_content.decode('utf-8', errors='replace')
    except Exception as e:
        raise ValueError(f"Unable to read file content: {str(e)}")

def run_simple_dashboard():
    # Initialize session state
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = None
    if 'current_file' not in st.session_state:
        st.session_state.current_file = None

    st.set_page_config(
        page_title="Analisis Chat Collection",
        page_icon="💬",
        layout="wide"
    )
    
    st.title("📊 Analisis Chat Collection")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Unggah file riwayat chat CSV",
        type="csv",
        help="Unggah file riwayat chat collection dalam format CSV"
    )
    
    if not uploaded_file and not st.session_state.analysis_result:
        st.info("👈 Silakan unggah file riwayat chat collection")
        return
        
    # Only process the file if it's newly uploaded or there's no analysis result yet
    if uploaded_file and (not st.session_state.analysis_result or 
                         st.session_state.current_file != uploaded_file.name):
        try:
            # Save uploaded file temporarily
            temp_path = Path(f"temp_{uploaded_file.name}")
            file_content = uploaded_file.read()
            temp_path.write_bytes(file_content)
            
            with st.spinner("Menganalisis chat..."):
                # Initialize analyzer
                analyzer = SimpleCollectionAnalyzer()
                # Analyze chat
                analysis = analyzer.analyze_chat(str(temp_path))
            
            # Clean up temp file
            temp_path.unlink()

            # Store results in session state
            st.session_state.analysis_result = analysis
            st.session_state.current_file = uploaded_file.name
            
            # Store raw content for chat history with proper encoding handling
            try:
                st.session_state.chat_history = read_file_content(file_content)
            except Exception as e:
                st.warning(f"Warning: Could not properly decode chat history: {str(e)}")
                st.session_state.chat_history = None
            
        except Exception as e:
            st.error(f"Error memproses file: {str(e)}")
            return

    # Use stored analysis result for display
    if st.session_state.analysis_result:
        analysis = st.session_state.analysis_result
        
        # Display Basic Information
        st.subheader("📋 Informasi Nasabah")
        col1, col2 = st.columns(2)
        with col1:
            if analysis.customer_info.name:
                st.info(f"👤 Nama: {analysis.customer_info.name}")
            if analysis.customer_info.agreement_number:
                st.info(f"📄 No. Perjanjian: {analysis.customer_info.agreement_number}")
        with col2:
            if analysis.customer_info.product:
                st.info(f"🏷️ Produk: {analysis.customer_info.product}")
            if analysis.customer_info.overdue_amount:
                st.info(f"💰 Tunggakan: Rp {analysis.customer_info.overdue_amount:,.0f}")
        
        # Display Promise Analysis
        col3, col4 = st.columns([2, 3])
        
        with col3:
            st.subheader("💳 Status Janji Bayar")
            if analysis.payment_promise.has_promise:
                st.success(
                    f"✅ Terdeteksi janji bayar (Tingkat keyakinan: {analysis.payment_promise.confidence_score:.0%})"
                )
                if analysis.payment_promise.promise_date:
                    st.info(f"📅 Tanggal Janji: {analysis.payment_promise.promise_date.strftime('%d/%m/%Y')}")
                if analysis.payment_promise.promise_amount:
                    st.info(f"💰 Jumlah Janji: Rp {analysis.payment_promise.promise_amount:,.0f}")
                
                if analysis.payment_promise.promise_messages:
                    st.subheader("💬 Pesan Janji Bayar")
                    for msg in analysis.payment_promise.promise_messages:
                        st.write(f"💬 {msg}")
            else:
                st.error("❌ Tidak terdeteksi janji bayar")
                
        with col4:
            st.subheader("📝 Rekomendasi Tindakan")
            for rec in analysis.recommendations:
                if rec.priority == "tinggi":
                    st.error(f"🔴 {rec.action}\n*Alasan:* {rec.reason}")
                elif rec.priority == "sedang":
                    st.warning(f"🟡 {rec.action}\n*Alasan:* {rec.reason}")
                else:
                    st.info(f"🔵 {rec.action}\n*Alasan:* {rec.reason}")
                    
        # Display summary
        st.subheader("📋 Ringkasan Analisis")
        st.write(analysis.summary)
        
        # Chat history viewer in expander
        with st.expander("📱 Lihat Riwayat Chat", expanded=False):
            if st.session_state.chat_history:
                try:
                    st.markdown("---")
                    messages = st.session_state.chat_history.strip().split('\n')
                    for message in messages:
                        if message.strip():  # Skip empty lines
                            try:
                                parts = message.split(';')
                                if len(parts) >= 3:
                                    sender, content, timestamp = parts[:3]
                                    st.write(f"**{timestamp}** - *{sender}*")
                                    st.write(f"{content}")
                                    st.markdown("---")
                                else:
                                    st.write(message)
                                    st.markdown("---")
                            except Exception as e:
                                st.write(message)
                                st.markdown("---")
                except Exception as e:
                    st.error(f"Error menampilkan chat: {str(e)}")
            else:
                st.warning("Riwayat chat tidak tersedia")

if __name__ == "__main__":
    run_simple_dashboard()