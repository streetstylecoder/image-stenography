# Import necessary libraries
from PIL import Image
import streamlit as st

# Convert encoding data into 8-bit binary
def genData(data):
    newd = [format(ord(i), '08b') for i in data]
    return newd

# Pixels are modified according to the 8-bit binary data and finally returned
def modPix(pix, data):
    datalist = genData(data)
    lendata = len(datalist)
    imdata = iter(pix)

    for i in range(lendata):
        pix = [value for value in imdata.__next__()[:3] +
                            imdata.__next__()[:3] +
                            imdata.__next__()[:3]]

        for j in range(0, 8):
            if (datalist[i][j] == '0' and pix[j] % 2 != 0):
                pix[j] -= 1
            elif (datalist[i][j] == '1' and pix[j] % 2 == 0):
                if (pix[j] != 0):
                    pix[j] -= 1
                else:
                    pix[j] += 1

        if (i == lendata - 1):
            if (pix[-1] % 2 == 0):
                if (pix[-1] != 0):
                    pix[-1] -= 1
                else:
                    pix[-1] += 1
        else:
            if (pix[-1] % 2 != 0):
                pix[-1] -= 1

        pix = tuple(pix)
        yield pix[0:3]
        yield pix[3:6]
        yield pix[6:9]

# Encode data into image
def encode_image(img, data):
    newimg = img.copy()
    w = newimg.size[0]
    encode_data = modPix(newimg.getdata(), data)
    newimg.putdata(list(encode_data))
    return newimg

# Decode the data in the image
def decode_image(img):
    image = Image.open(img, 'r')
    data = ''
    imgdata = iter(image.getdata())
    while True:
        pixels = [value for value in imgdata.__next__()[:3] +
                                imgdata.__next__()[:3] +
                                imgdata.__next__()[:3]]
        binstr = ''
        for i in pixels[:8]:
            if i % 2 == 0:
                binstr += '0'
            else:
                binstr += '1'
        data += chr(int(binstr, 2))
        if pixels[-1] % 2 != 0:
            return data

def encrypt(text, s):
    result = ""
    for i in range(len(text)):
        char = text[i]
        if char.isupper():
            result += chr((ord(char) + s - 65) % 26 + 65)
        elif char.islower():
            result += chr((ord(char) + s - 97) % 26 + 97)
        else:
            result += char
    return result

# Streamlit UI
st.title("Image Steganography - by Anshika")

uploaded_file = st.file_uploader("Upload Image")
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_column_width=True)

    st.subheader("Image Options")
    option = st.selectbox("Choose an option:", ("Encode", "Decode"))

    if option == "Encode":
        st.subheader("Encode Message in Image")
        message = st.text_input("Enter the message to hide:")
        private_key = st.number_input("Enter the private key:", value=0, step=1)
        if st.button("Encode"):
            if message:
                encrypted_message = encrypt(message, private_key)
                new_image = encode_image(image, encrypted_message)
                st.image(new_image, caption='Encoded Image', use_column_width=True)
                st.markdown("### Download Encoded Image")
                st.image(new_image, output_format='PNG', use_column_width=True)

    elif option == "Decode":
        st.subheader("Decode Message from Image")
        private_key = st.number_input("Enter the private key:", value=0, step=1)
        if st.button("Decode"):
            decoded_message = decode_image(uploaded_file)
            decrypted_message = encrypt(decoded_message, -private_key)
            st.text_area("Decoded Message", value=decoded_message, height=200)
            st.text_area("Decrypted Message", value=decrypted_message, height=200)
