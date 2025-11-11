import streamlit as st
import random

# -----------------------------------------------------------
# Hill Cipher Encryption Tool (2x2 Matrix Version)
# Designed for Educational Demonstration
# -----------------------------------------------------------

# --- Configuration ---
st.set_page_config(
    page_title="Hill Cipher Encryption Tool",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for a clean, professional look ---
st.markdown("""
    <style>
        body {
            background-color: #0e1117;
            color: #f5f5f5;
        }
        .stApp {
            background-color: #0e1117;
        }
        h1, h2, h3, h4 {
            color: #ffffff !important;
            font-weight: 700;
        }
        .stTextArea textarea {
            background-color: #1e2229;
            color: white;
            border-radius: 10px;
            border: 1px solid #30343a;
            font-size: 16px;
        }
        .stButton>button {
            background-color: #2563eb;
            color: white;
            border-radius: 10px;
            border: none;
            font-weight: 600;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #1d4ed8;
            color: #e5e5e5;
        }
        .css-1d391kg, .css-18e3th9 {
            background-color: #111418 !important;
        }
        table {
            background-color: #1b1f25;
            color: #f5f5f5;
            border-radius: 8px;
        }
        .footer {
            text-align: center;
            color: #a3a3a3;
            font-size: 14px;
            margin-top: 50px;
        }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# Mapping and Constants
# -----------------------------------------------------------

letter_to_num = {chr(i + 65): i for i in range(26)}
num_to_letter = {i: chr(i + 65) for i in range(26)}

mod_inverse = {
    1: 1, 3: 9, 5: 21, 7: 15, 9: 3, 11: 19,
    15: 7, 17: 23, 19: 11, 21: 5, 23: 17, 25: 25
}

# -----------------------------------------------------------
# Utility Functions
# -----------------------------------------------------------

def find_inverse(a):
    """Find modular inverse of determinant (mod 26)."""
    a = a % 26
    if a in mod_inverse:
        return mod_inverse[a]
    else:
        raise ValueError(f"No modular inverse exists for determinant {a} (mod 26).")


def inverse_matrix_mod26(K):
    """Compute inverse of 2x2 key matrix (mod 26)."""
    a, b = K[0][0], K[0][1]
    c, d = K[1][0], K[1][1]
    det = (a * d - b * c) % 26
    inv_det = find_inverse(det)
    adj = [[d, -b], [-c, a]]
    K_inv = [[(inv_det * adj[i][j]) % 26 for j in range(2)] for i in range(2)]
    return K_inv


def text_to_numbers(text):
    """Convert text to numeric list (A-Z only)."""
    return [letter_to_num[ch] for ch in text.upper() if ch.isalpha()]


def numbers_to_text(nums):
    """Convert numeric list back to text."""
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
    """Encrypt full text using Hill Cipher."""
    plaintext = plaintext.upper().replace(" ", "")
    if len(plaintext) % 2 != 0:
        plaintext += "X"
    ciphertext = ""
    for i in range(0, len(plaintext), 2):
        ciphertext += encrypt_block(plaintext[i:i+2], K)
    return ciphertext


def decrypt_text(ciphertext, K_inv):
    """Decrypt full text."""
    ciphertext = ciphertext.upper().replace(" ", "")
    plaintext = ""
    for i in range(0, len(ciphertext), 2):
        plaintext += decrypt_block(ciphertext[i:i+2], K_inv)
    return plaintext


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
# Streamlit Layout
# -----------------------------------------------------------

st.title("Matrix Encryption & Translation Tool")
st.markdown("### Hill Cipher Implementation using Invertible Matrices and Modular Arithmetic")

st.write("""
This web-based demonstration applies **Linear Algebra concepts**—specifically matrix multiplication,
determinants, and modular arithmetic—to implement the **Hill Cipher**, an early form of polygraphic substitution cipher.
""")

st.divider()

# Sidebar – Key Matrix
st.sidebar.header("Encryption Key Configuration")
key_mode = st.sidebar.radio("Select Key Option", ["Generate Random Key", "Enter Manually"])

if key_mode == "Generate Random Key":
    key_matrix = generate_random_key()
    st.sidebar.success("Random invertible key generated successfully.")
else:
    st.sidebar.info("Enter integers between 0 and 25:")
    a = st.sidebar.number_input("K[0][0]", 0, 25, 3)
    b = st.sidebar.number_input("K[0][1]", 0, 25, 3)
    c = st.sidebar.number_input("K[1][0]", 0, 25, 2)
    d = st.sidebar.number_input("K[1][1]", 0, 25, 5)
    key_matrix = [[a, b], [c, d]]

st.sidebar.write("### Current Key Matrix")
st.sidebar.table(key_matrix)

# Validate invertibility
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
            st.warning("Please enter text for encryption.")
        else:
            ciphertext = encrypt_text(plaintext, key_matrix)
            st.success("Ciphertext:")
            st.code(ciphertext, language="text")

with col2:
    st.subheader("Decrypt")
    ciphertext_input = st.text_area("Enter text to decrypt:", "")
    if st.button("Decrypt"):
        if not valid_key:
            st.error("Please enter a valid invertible key matrix.")
        elif not ciphertext_input.strip():
            st.warning("Please enter text for decryption.")
        else:
            decrypted = decrypt_text(ciphertext_input, key_inverse)
            st.success("Decrypted Text:")
            st.code(decrypted, language="text")

st.divider()
st.markdown("<p class='footer'>Developed by Group 11 – B.Tech CSE, BML Munjal University (2025)</p>", unsafe_allow_html=True)
