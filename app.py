# app.py
import streamlit as st
import random
import re
import pandas as pd

# ---------------------------
# Streamlit page config
# ---------------------------
st.set_page_config(page_title="Hill Cipher Encryption Tool", layout="wide")

# ---------------------------
# Styling (minimal, professional)
# ---------------------------
st.markdown(
    """
    <style>
      .stApp { background-color: #0e1117; color: #f5f5f5; }
      .stTextArea textarea { background-color: #151719; color: #eaeaea; border-radius: 8px; }
      .stButton > button { background-color: #2563eb; color: white; border-radius: 8px; }
      .stTable table { background-color: #121417; color: #eaeaea; }
      .footer { text-align:center; color:#9aa0a6; margin-top:40px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Constants and Mappings (classic A-Z, mod 26)
# ---------------------------
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
modulus = 26

letter_to_num = {alphabet[i]: i for i in range(modulus)}
num_to_letter = {i: alphabet[i] for i in range(modulus)}

# precomputed modular inverses mod 26 for numbers coprime with 26
mod_inverse = {
    1: 1, 3: 9, 5: 21, 7: 15, 9: 3, 11: 19,
    15: 7, 17: 23, 19: 11, 21: 5, 23: 17, 25: 25
}

# ---------------------------
# Helper functions
# ---------------------------

def find_inverse(a):
    a = a % modulus
    if a in mod_inverse:
        return mod_inverse[a]
    raise ValueError(f"No modular inverse for determinant {a} mod {modulus}.")

def inverse_matrix_mod26(K):
    a, b = K[0][0], K[0][1]
    c, d = K[1][0], K[1][1]
    det = (a * d - b * c) % modulus
    inv_det = find_inverse(det)
    adj = [[d, -b], [-c, a]]
    K_inv = [[(inv_det * adj[i][j]) % modulus for j in range(2)] for i in range(2)]
    return K_inv

def clean_text_keep_alpha(text: str):
    """Return uppercase string containing only A-Z (no spaces/punct)."""
    cleaned = re.sub(r'[^A-Za-z]', '', text).upper()
    return cleaned

def pad_text(text: str):
    """Pad with 'X' if needed to make even length for 2x2 Hill."""
    if len(text) % 2 != 0:
        return text + "X"
    return text

def text_to_numbers(text: str):
    return [letter_to_num[ch] for ch in text]

def numbers_to_text(nums):
    return ''.join(num_to_letter[n % modulus] for n in nums)

def encrypt_block(block: str, K):
    p = text_to_numbers(block)
    c1 = (K[0][0] * p[0] + K[0][1] * p[1]) % modulus
    c2 = (K[1][0] * p[0] + K[1][1] * p[1]) % modulus
    return numbers_to_text([c1, c2]), [c1, c2], [p[0], p[1]]

def decrypt_block(block: str, K_inv):
    c = text_to_numbers(block)
    p1 = (K_inv[0][0] * c[0] + K_inv[0][1] * c[1]) % modulus
    p2 = (K_inv[1][0] * c[0] + K_inv[1][1] * c[1]) % modulus
    return numbers_to_text([p1, p2]), [p1, p2], [c[0], c[1]]

def encrypt_full(plaintext: str, K):
    cleaned = clean_text_keep_alpha(plaintext)
    padded = pad_text(cleaned)
    ciphertext = ""
    blocks = []
    for i in range(0, len(padded), 2):
        block = padded[i:i+2]
        ctext, cnums, pnums = encrypt_block(block, K)
        ciphertext += ctext
        blocks.append({"plain_block": block, "plain_nums": pnums, "cipher_nums": cnums, "cipher_block": ctext})
    return cleaned, padded, ciphertext, blocks

def decrypt_full(ciphertext: str, K_inv):
    cleaned = clean_text_keep_alpha(ciphertext)
    if len(cleaned) % 2 != 0:
        # ciphertext should be even length; warn but proceed by ignoring last char
        cleaned = cleaned[:-1]  # avoid index errors
    plaintext = ""
    blocks = []
    for i in range(0, len(cleaned), 2):
        block = cleaned[i:i+2]
        ptext, pnums, cnums = decrypt_block(block, K_inv)
        plaintext += ptext
        blocks.append({"cipher_block": block, "cipher_nums": cnums, "plain_nums": pnums, "plain_block": ptext})
    return cleaned, plaintext, blocks

def generate_random_key():
    while True:
        K = [[random.randint(0,25), random.randint(0,25)],
             [random.randint(0,25), random.randint(0,25)]]
        try:
            _ = inverse_matrix_mod26(K)
            return K
        except Exception:
            continue

# ---------------------------
# Session state initialization
# ---------------------------
if "key_matrix" not in st.session_state:
    st.session_state.key_matrix = [[3,3],[2,5]]  # default
if "key_inverse" not in st.session_state:
    try:
        st.session_state.key_inverse = inverse_matrix_mod26(st.session_state.key_matrix)
    except Exception:
        st.session_state.key_inverse = None
if "last_cipher" not in st.session_state:
    st.session_state.last_cipher = ""

# ---------------------------
# UI layout
# ---------------------------
st.title("Matrix Encryption & Translation Tool")
st.markdown("Hill Cipher (2×2) — Invertible matrices & modular arithmetic")

st.divider()

# Sidebar: key config
with st.sidebar:
    st.header("Encryption Key Configuration")
    key_option = st.radio("Select Key Option", ["Generate Random Key", "Enter Manually"])

    if key_option == "Generate Random Key":
        if st.button("Generate Random Invertible Key"):
            st.session_state.key_matrix = generate_random_key()
            st.session_state.key_inverse = inverse_matrix_mod26(st.session_state.key_matrix)
            st.success("Random invertible key generated.")
    else:
        st.info("Enter integers (0–25) for each key element")
        a = st.number_input("K[0][0]", 0, 25, int(st.session_state.key_matrix[0][0]))
        b = st.number_input("K[0][1]", 0, 25, int(st.session_state.key_matrix[0][1]))
        c = st.number_input("K[1][0]", 0, 25, int(st.session_state.key_matrix[1][0]))
        d = st.number_input("K[1][1]", 0, 25, int(st.session_state.key_matrix[1][1]))
        if st.button("Set Key"):
            st.session_state.key_matrix = [[int(a), int(b)], [int(c), int(d)]]
            try:
                st.session_state.key_inverse = inverse_matrix_mod26(st.session_state.key_matrix)
                st.success("Key set and invertible.")
            except Exception:
                st.session_state.key_inverse = None
                st.error("Key set but not invertible (determinant has no inverse mod 26).")

    st.markdown("### Current Key Matrix")
    key_df = pd.DataFrame(st.session_state.key_matrix, index=["0","1"], columns=["0","1"])
    st.table(key_df)

# main columns
col_enc, col_dec = st.columns([1,1])

# Encryption panel
with col_enc:
    st.subheader("Encrypt")
    with st.form("encrypt_form", clear_on_submit=False):
        plaintext = st.text_area("Enter text to encrypt:", height=140)
        enc_submit = st.form_submit_button("Encrypt")
        if enc_submit:
            if st.session_state.key_inverse is None:
                st.error("Current key is not invertible. Generate or enter a valid key.")
            else:
                cleaned, padded, ciphertext, blocks = encrypt_full(plaintext, st.session_state.key_matrix)
                st.session_state.last_cipher = ciphertext
                if cleaned == "":
                    st.error("No alphabetic characters found in input. Please enter letters A–Z.")
                else:
                    if cleaned != plaintext.upper().replace(" ", "").replace("\n",""):
                        st.info("Note: non-alphabet characters were removed before encryption (spaces, punctuation, digits).")
                    st.markdown("**Cleaned Plaintext (A–Z only):**")
                    st.code(cleaned)
                    st.markdown("**Padded Plaintext (blocks of 2):**")
                    st.code(padded)
                    st.markdown("**Ciphertext:**")
                    st.success(ciphertext)
                    if blocks:
                        df_blocks = pd.DataFrame(blocks)
                        # show numeric columns nicely
                        df_blocks["plain_nums"] = df_blocks["plain_nums"].apply(lambda x: str(x))
                        df_blocks["cipher_nums"] = df_blocks["cipher_nums"].apply(lambda x: str(x))
                        st.markdown("**Block-wise details:**")
                        st.table(df_blocks[["plain_block","plain_nums","cipher_nums","cipher_block"]])

# Decryption panel
with col_dec:
    st.subheader("Decrypt")
    with st.form("decrypt_form", clear_on_submit=False):
        ciphertext_input = st.text_area("Enter text to decrypt (or paste ciphertext):", value=st.session_state.last_cipher, height=140)
        dec_submit = st.form_submit_button("Decrypt")
        if dec_submit:
            if st.session_state.key_inverse is None:
                st.error("Current key is not invertible. Generate or enter a valid key.")
            else:
                cleaned_ct, plaintext, blocks = decrypt_full(ciphertext_input, st.session_state.key_inverse)
                if cleaned_ct == "":
                    st.error("No alphabetic characters found in ciphertext. Please paste valid ciphertext (A–Z).")
                else:
                    st.markdown("**Cleaned Ciphertext (A–Z only):**")
                    st.code(cleaned_ct)
                    st.markdown("**Decrypted plaintext (may include padding 'X'):**")
                    st.success(plaintext)
                    if blocks:
                        df_blocks = pd.DataFrame(blocks)
                        df_blocks["cipher_nums"] = df_blocks["cipher_nums"].apply(lambda x: str(x))
                        df_blocks["plain_nums"] = df_blocks["plain_nums"].apply(lambda x: str(x))
                        st.markdown("**Block-wise details:**")
                        st.table(df_blocks[["cipher_block","cipher_nums","plain_nums","plain_block"]])

st.divider()
st.markdown("<div class='footer'>Developed by Group 11 – B.Tech CSE, BML Munjal University (2025)</div>", unsafe_allow_html=True)
