import streamlit as st
import random
import re

# -----------------------------------------------------------
# Hill Cipher Encryption Tool (2x2 Matrix, Classic A–Z)
# Professional and Error-Resilient Version
# -----------------------------------------------------------

# ---------- Streamlit Setup ----------
st.set_page_config(page_title="Hill Cipher Encryption Tool", layout="wide")

# ---------- Custom Styling ----------
st.markdown("""
    <style>
        .stApp {background-color: #0e1117;}
        h1, h2, h3, h4 {color: #ffffff; font-weight: 700;}
        .stTextArea textarea {
            background-color: #1e2229; color: white;
            border-radius: 10px; border: 1px solid #30343a; font-size: 16px;
        }
        .stButton>button {
            background-color: #2563eb; color: white; border-radius: 8px;
            border: none; font-weight: 600; transition: 0.3s;
        }
        .stButton>button:hover {background-color: #1d4ed8;}
        .footer {text-align:center; color:#a3a3a3; margin-top:40px;}
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# Hill Cipher Core Logic (mod 26, A–Z only)
# -----------------------------------------------------------

letter_to_num = {chr(i + 65): i for i in range(26)}
num_to_letter = {i: chr(i + 65) for i in range(26)}

mod_inverse = {
    1: 1, 3: 9, 5: 21, 7: 15, 9: 3, 11: 19,
    15: 7, 17: 23, 19: 11, 21: 5, 23: 17, 25: 25
}


def find_inverse(a):
    """Find modular inverse of determinant (mod 26)."""
    a = a % 26
    if a in mod_inverse:
        return mod_inverse[a]
    raise ValueError(f"No modular inverse for determinant {a} mod 26.")


def inverse_matrix_mod26(K):
    """Compute inverse of 2x2 key matrix under mod 26."""
    a, b = K[0][0], K[0][1]
    c, d = K[1][0], K[1][1]
    det = (a * d - b * c) % 26
    inv_det = find_inverse(det)
    adj = [[d, -b], [-c, a]]
    K_inv = [[(inv_det * adj[i][j]) % 26 for j in range(2)] for i in range(2)]
    return K_inv


def clean_text(text):
    """
    Converts input text to uppercase and removes non-alphabet characters.
    Returns cleaned text and a flag if any cleaning occurred.
    """
    cleaned = re.sub(r'[^A-Za-z]', '', text).upper()
    cleaned_flag = cleaned != text.upper()
    return cleaned, cleaned_flag


def text_to_numbers(text):
    """Convert text (A–Z) to numeric list (0–25)."""
    return [letter_to_num[ch] for ch in text]


def numbers_to_text(nums):
    """Convert numeric list (0–25) to uppercase letters."""
    return ''.join(num_to_letter[n % 26] for n in nums)


def encrypt_block(block, K):
    """Encrypt a 2-letter block."""
    p = text_to_numbers(block)
    c1 = (K[0][0] * p[0] + K[0][1] * p[1]) % 26
    c2 = (K[1][0] * p[0] + K[1][1] * p[1]) % 26
    return numbers_to_text([c1, c2])


def decrypt_block(block, K_inv):
    """Decrypt a 2-letter block."""
    c = text_to_numbers(block)
    p1 = (K_inv[0][0] * c[0] + K_inv[0][1] * c[1]) % 26
    p2 = (K_inv[1][0] * c[0] + K_inv[1][1] * c[1]) % 26
    return numbers_to_text([p1, p2])


def encrypt_text(plaintext, K):
    """Encrypt full cleaned text, adding padding if odd length."""
    plaintext, was_cleaned = clean_text(plaintext)
    if not plaintext:
        raise ValueError("Text must contain at least one alphabetic character.")
    if len(plaintext) % 2 != 0:
        plaintext += "X"
    ciphertext = "".join(encrypt_block(plaintext[i:i+2], K)
                         for i in range(0, len(plaintext), 2))
    return ciphertext, was_cleaned


def decrypt_text(ciphertext, K_inv):
    """Decrypt full cleaned text."""
    ciphertext, was_cleaned = clean_text(ciphertext)
    if not ciphertext:
        raise ValueError("Ciphertext must contain at least one alphabetic character.")
    plaintext = "".join(decrypt_block(ciphertext[i:i+2], K_inv)
                        for i in range(0, len(ciphertext), 2))
    return plaintext, was_cleaned


def generate_random_key():
    """Generate random invertible 2x2 matrix."""
    while True:
        K = [[random.randint(0, 25), random.randint(0, 25)],
             [random.randint(0, 25), random.randint(0, 25)]]
        try:
            _ = inverse_matrix_mod26(K)
            return K
        except Exception:
            continue

# -----------------------------------------------------------
# Streamlit UI
# -----------------------------------------------------------

st.title("Matrix Encryption & Translation Tool")
st.markdown("### Hill Cipher – Using Invertible Matrices and Modular Arithmetic")

st.write("""
This demonstration implements the **Hill Cipher**, a classical encryption technique
that applies concepts from *Linear Algebra*—including matrix multiplication, determinants, 
and inverses—to achieve secure text encoding.
""")

st.divider()

# Sidebar: Key matrix input
st.sidebar.header("Encryption Key Configuration")
key_option = st.sidebar.radio("Select Key Option", ["Generate Random Key", "Enter Manually"])

if key_option == "Generate Random Key":
    key_matrix = generate_random_key()
    st.sidebar.success("Random invertible key generated successfully.")
else:
    st.sidebar.info("Enter integer values (0–25):")
    a = st.sidebar.number_input("K[0][0]", 0, 25, 3)
    b = st.sidebar.number_input("K[0][1]", 0, 25, 3)
    c = st.sidebar.number_input("K[1][0]", 0, 25, 2)
    d = st.sidebar.number_input("K[1][1]", 0, 25, 5)
    key_matrix = [[a, b], [c, d]]

st.sidebar.write("### Current Key Matrix")
st.sidebar.table(key_matrix)

# Validate key
try:
    key_inverse = inverse_matrix_mod26(key_matrix)
    valid_key = True
except Exception:
    st.sidebar.error("Invalid key: determinant not invertible mod 26.")
    valid_key = False

st.divider()

# Two-column layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Encrypt")
    plaintext = st.text_area("Enter text to encrypt:", "")
    if st.button("Encrypt"):
        if not valid_key:
            st.error("Please enter a valid invertible key matrix.")
        elif not plaintext.strip():
            st.warning("Please enter text to encrypt.")
        else:
            try:
                ciphertext, cleaned = encrypt_text(plaintext, key_matrix)
                if cleaned:
                    st.info("Note: Non-alphabet characters were removed automatically before encryption.")
                st.success("Ciphertext:")
                st.code(ciphertext, language="text")
            except Exception as e:
                st.error(str(e))

with col2:
    st.subheader("Decrypt")
    ciphertext_input = st.text_area("Enter text to decrypt:", "")
    if st.button("Decrypt"):
        if not valid_key:
            st.error("Please enter a valid invertible key matrix.")
        elif not ciphertext_input.strip():
            st.warning("Please enter text to decrypt.")
        else:
            try:
                decrypted, cleaned = decrypt_text(ciphertext_input, key_inverse)
                if cleaned:
                    st.info("Note: Non-alphabet characters were removed automatically before decryption.")
                st.success("Decrypted Text:")
                st.code(decrypted, language="text")
            except Exception as e:
                st.error(str(e))

st.divider()
st.markdown("<p class='footer'>Developed by Group 11 – B.Tech CSE, BML Munjal University (2025)</p>", unsafe_allow_html=True)
