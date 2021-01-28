#
# class Korean()
# 영문으로 입력된 문자를 한글로 처리하는 클래스
#

# 입력이 자음인지 모음인지 구분하기 위한 튜플
CONSONANT = ('r','R','s','S','e','E','f','F','a','A','q','Q','t','T','d','D','w','W','c','C','z','Z','x','X','v','V','g','G')
VOWEL = ('k','K','o','O','i','I','j','J','p','P','u','U','h','H','y','Y','n','N','b','B','m','M','l','L')

# 초성과 종성 그리고 종성 코드를 위한 튜플
CHOSEONG = ('r','R','s','e','E','f','a','q','Q','t','T','d','w','W','c','z','x','v','g')
JUNGSEONG = ('k','o','i','O','j','p','u','P','h','hk','ho','hl','y','n','nj','np','nl','b','m','ml','l')
JONGSEONG = ('','r','R','rt','s','sw','sg','e','f','fr','fa','fq','ft','fx','fv','fg','a','q','qt','t','T','d','w','c','z','x','v','g')

# 음소 단위로 처리하기 위한 튜플
PHOENMES = (
    'r','R','rt','s','sw','sg','e','E','f','fr','fa','fq','ft','fx','fv','fg',
    'a','q','Q','qt','t','T','d','w','W','c','z','x','v','g','k','o','i','O',
    'j','p','u','P','h','hk','ho','hl','y','n','nj','np','nl','b','m','ml','l'
    )

# 대문자에 해당하는 키를 눌러서 입력하는 자음과 모음
UPPER_CASE = ('Q','W','E','R','T','O','P')

# 유니코드의 베이스 코드 음소 단위(12593), 완성형 글자(44032)
BASE_CODE = (12593, 44032)

class Korean:
    def __init__(self, koreanMode=False, multiLine=False):
        self.text = ""
        self.combineChar = ""
        self.status = ""
        self.cursor = 0
        self.selectionStart = 0
        self.selectionEnd = 0
        self.koreanMode = koreanMode
        self.multiLine = multiLine

    def Input(self, char):
        if self.selectionStart != self.selectionEnd:
            self.text = self.text[:self.selectionStart] + self.text[self.selectionEnd:]
            self.cursor = self.selectionEnd = self.selectionStart
        if self.koreanMode:
            self.processKoreanInput(char if char in UPPER_CASE else char.lower())
        else:
            if self.status != "":
                self.text = self.text[:self.selectionStart] + self.combine() + self.text[self.selectionEnd:]
                self.status = self.combineChar = ""
                self.cursor += 1
                self.selectionStart = self.selectionEnd = self.cursor
            self.text = self.text[:self.selectionStart] + char + self.text[self.selectionEnd:]
            self.cursor += 1
            self.selectionStart = self.selectionEnd = self.cursor

    def Delete(self, backspace=False):
        print("delete", backspace)
        if backspace:
            pass
        else:
            if self.selectionStart == self.selectionEnd:
                self.text = self.text[:self.selectionStart] + self.text[self.selectionEnd+1:]
            else:
                self.text = self.text[:self.selectionStart] + self.text[self.selectionEnd:]
                self.cursor = self.selectionEnd = self.selectionStart

    def MoveLeft(self, shift=False):
        if shift:
            if self.selectionStart == self.selectionEnd:
                if self.status == "":
                    self.cursor = max(0, self.cursor-1)
                    self.selectionStart = self.cursor
                else:
                    self.text = self.text[:self.selectionStart] + self.combine() + self.text[self.selectionEnd:]
                    self.status = self.combineChar = ""
                    self.selectionEnd += 1
            else:
                if self.cursor == self.selectionStart:
                    self.cursor = max(0, self.cursor-1)
                    self.selectionStart = self.cursor
                else:
                    self.cursor = max(0, self.cursor-1)
                    self.selectionEnd = self.cursor
        else:
            if self.selectionStart == self.selectionEnd:
                if self.status == "":
                    self.cursor = max(0, self.cursor-1)
                else:
                    self.text = self.text[:self.selectionStart] + self.combine() + self.text[self.selectionEnd:]
                    self.status = self.combineChar = ""
                self.selectionStart = self.selectionEnd = self.cursor
            else:
                self.cursor = self.selectionEnd = self.selectionStart

    def MoveRight(self, shift=False):
        if shift:
            if self.selectionStart == self.selectionEnd:
                if self.status != "":
                    self.text = self.text[:self.selectionStart] + self.combine() + self.text[self.selectionEnd:]
                    self.status = self.combineChar = ""
                    self.cursor += 1
                    self.selectionStart = self.selectionEnd = self.cursor
                self.cursor = min(len(self.text), self.cursor+1)
                self.selectionEnd = self.cursor
            else:
                if self.cursor == self.selectionStart:
                    self.cursor = min(len(self.text), self.cursor+1)
                    self.selectionStart = self.cursor
                else:
                    self.cursor = min(len(self.text), self.cursor+1)
                    self.selectionEnd = self.cursor
        else:
            if self.selectionStart == self.selectionEnd:
                if self.status != "":
                    self.text = self.text[:self.selectionStart] + self.combine() + self.text[self.selectionEnd:]
                    self.status = self.combineChar = ""
                self.cursor = min(len(self.text), self.cursor+1)
                self.selectionStart = self.selectionEnd = self.cursor
            else:
                self.cursor = self.selectionStart = self.selectionEnd

    def GetMode(self):
        return self.koreanMode

    def SetMode(self, mode):
        if self.status != "":
            self.text = self.text[:self.selectionStart] + self.combine() + self.text[self.selectionEnd:]
            self.status = self.combineChar = ""
            self.cursor += 1
            self.selectionStart = self.selectionEnd = self.cursor
        self.koreanMode = mode

    def SetText(self, text):
        self.text = text
        self.selectionStart = 0
        self.selectionEnd = self.cursor = len(text)

    def GetText(self):
        if self.status != "":
            return self.text[:self.selectionStart] + self.combine() + self.text[self.selectionEnd:]
        return self.text

    def processKoreanInput(self, char):
        cType = self.getType(char)
        if cType == 'C':
            self.processConsonant(char)
        elif cType == 'V':
            self.processVowel(char)
        else:
            if self.status != "":
                self.text = self.text[:self.selectionStart] + self.combine() + self.text[self.selectionEnd:]
                self.status = self.combineChar = ""
                self.cursor += 1
                self.selectionStart = self.selectionEnd = self.cursor
            self.text = self.text[:self.selectionStart] + char + self.text[self.selectionEnd:]
            self.cursor += 1
            self.selectionStart = self.selectionEnd = self.cursor

    def processConsonant(self, char):
        if self.status == "":
            self.status = "C"
            self.combineChar = char
        elif self.status == "C":
            dc = self.combineChar + char
            if dc in PHOENMES:
                self.status += "C"
                self.combineChar += char
            else:
                self.text = self.text[:self.selectionStart] + self.combine() + self.text[self.selectionEnd:]
                self.cursor += 1
                self.selectionStart = self.selectionEnd = self.cursor
                self.status = "C"
                self.combineChar = char
        elif self.status in {"CC", "V", "VV"}:
            self.text = self.text[:self.selectionStart] + self.combine() + self.text[self.selectionEnd:]
            self.cursor += 1
            self.selectionStart = self.selectionEnd = self.cursor
            self.status = "C"
            self.combineChar = char
        elif self.status in {"CV", "CVV"}:
            self.status += "C"
            self.combineChar += char
        elif self.status in {"CVC", "CVVC"}:
            dc = self.combineChar[-1] + char
            if dc in PHOENMES:
                self.status += "C"
                self.combineChar += char
            else:
                self.text = self.text[:self.selectionStart] + self.combine() + self.text[self.selectionEnd:]
                self.cursor += 1
                self.selectionStart = self.selectionEnd = self.cursor
                self.status = "C"
                self.combineChar = char

    def processVowel(self, char):
        if self.status == "":
            self.status = "V"
            self.combineChar = char
        elif self.status == "C":
            self.status += "V"
            self.combineChar += char
        elif self.status == "V":
            dc = self.combineChar + char
            if dc in PHOENMES:
                self.status += "V"
                self.combineChar += char
            else:
                self.text = self.text[:self.selectionStart] + self.combine() + self.text[self.selectionEnd:]
                self.cursor += 1
                self.selectionStart = self.selectionEnd = self.cursor
                self.status = "V"
                self.combineChar = char
        elif self.status == "CC":
            second_char = self.combineChar[1]
            self.combineChar = self.combineChar[0]
            self.text = self.text[:self.selectionStart] + self.combine() + self.text[self.selectionEnd:]
            self.cursor += 1
            self.selectionStart = self.selectionEnd = self.cursor
            self.status = "V"
            self.combineChar = char
        elif self.status == "CV":
            dc = self.combineChar[-1] + char
            if dc in PHOENMES:
                self.status += "V"
                self.combineChar += char
            else:
                self.text = self.text[:self.selectionStart] + self.combine() + self.text[self.selectionEnd:]
                self.cursor += 1
                self.selectionStart = self.selectionEnd = self.cursor
                self.status = "V"
                self.combineChar = char
        elif self.status in {"VV", "CVV"}:
            self.text = self.text[:self.selectionStart] + self.combine() + self.text[self.selectionEnd:]
            self.cursor += 1
            self.selectionStart = self.selectionEnd = self.cursor
            self.status = "V"
            self.combineChar = char
        elif self.status in {"CVC", "CVCC", "CVVC", "CVVCC"}:
            last_char = self.combineChar[-1]
            self.combineChar = self.combineChar[:len(self.combineChar)-1]
            self.status = self.status[:len(self.status)-1]
            self.text = self.text[:self.selectionStart] + self.combine() + self.text[self.selectionEnd:]
            self.cursor += 1
            self.selectionStart = self.selectionEnd = self.cursor
            self.status = "CV"
            self.combineChar = last_char + char

    def getType(self, char):
        if char in CONSONANT:
            return "C"
        elif char in VOWEL:
            return "V"
        return "N"

    def combine(self):
        if self.status in {"C", "V", "CC", "VV"}:
            return chr(BASE_CODE[0] + PHOENMES.index(self.combineChar))
        elif self.status == "CV":
            cho = CHOSEONG.index(self.combineChar[0])
            jung = JUNGSEONG.index(self.combineChar[1])
            return chr(BASE_CODE[1] + cho * 588 + jung * 28)
        elif self.status == "CVV":
            cho = CHOSEONG.index(self.combineChar[0])
            jung = JUNGSEONG.index(self.combineChar[1:3])
            return chr(BASE_CODE[1] + cho * 588 + jung * 28)
        elif self.status == "CVC":
            cho = CHOSEONG.index(self.combineChar[0])
            jung = JUNGSEONG.index(self.combineChar[1])
            jong = JONGSEONG.index(self.combineChar[2])
            return chr(BASE_CODE[1] + cho * 588 + jung * 28 + jong)
        elif self.status == "CVCC":
            cho = CHOSEONG.index(self.combineChar[0])
            jung = JUNGSEONG.index(self.combineChar[1])
            jong = JONGSEONG.index(self.combineChar[2:4])
            return chr(BASE_CODE[1] + cho * 588 + jung * 28 + jong)
        elif self.status == "CVVC":
            cho = CHOSEONG.index(self.combineChar[0])
            jung = JUNGSEONG.index(self.combineChar[1:3])
            jong = JONGSEONG.index(self.combineChar[3])
            return chr(BASE_CODE[1] + cho * 588 + jung * 28)
        elif self.status == "CVVCC":
            cho = CHOSEONG.index(self.combineChar[0])
            jung = JUNGSEONG.index(self.combineChar[1:3])
            jong = JONGSEONG.index(self.combineChar[3:5])
            return chr(BASE_CODE[1] + cho * 588 + jung * 28)
        return ""
