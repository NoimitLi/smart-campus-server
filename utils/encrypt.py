from Crypto.Cipher import AES
import base64

AES_KEY = 'smart-campus-aes-key'
IV = 'smart-campus-iv'
AES_MODE = 'CBC'


class AESHelper:
    def __init__(self, key=None, iv=None, mode=None):
        self.key = key or AES_KEY
        self.iv = iv or IV
        self.mode = mode or AES_MODE

    def _add_to_16(self, data) -> bytes:
        """Pad data to be a multiple of 16 bytes using PKCS7 padding"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        pad_len = 16 - (len(data) % 16)
        return data + bytes([pad_len] * pad_len)

    def _remove_padding(self, data) -> bytes:
        """Remove PKCS7 padding"""
        pad_len = data[-1]
        # Validate padding
        if pad_len > 16 or not all(b == pad_len for b in data[-pad_len:]):
            raise ValueError("Invalid padding")
        return data[:-pad_len]

    def aes_encrypt(self, data) -> str:
        """AES加密"""
        # 初始化加密器
        aes = AES.new(self._add_to_16(self.key), getattr(AES, f'MODE_{self.mode}'), self._add_to_16(self.iv))
        # 加密
        encrypt_aes = aes.encrypt(self._add_to_16(data))
        # 用base64转码返回str
        base64_str = base64.encodebytes(encrypt_aes).decode('utf-8').strip()
        return base64_str

    def aes_decrypt(self, data) -> str:
        """AES解密"""
        # 初始化加密器
        aes = AES.new(self._add_to_16(AES_KEY), getattr(AES, f'MODE_{AES_MODE}'), self._add_to_16(IV))
        # 优先用base64转码返回bytes
        decrypted = aes.decrypt(base64.b64decode(data))
        # 解密
        decrypt_str = self._remove_padding(decrypted).decode('utf-8')
        return decrypt_str


if __name__ == '__main__':
    aes_helper = AESHelper()
    print(aes_helper.aes_encrypt('123456'))
    print(aes_helper.aes_decrypt('3OPCgpNbf8jo3zzlkfT5ww=='))
