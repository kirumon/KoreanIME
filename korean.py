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
    def __init__(self, koreanMode=False, multi=False):
        self.combineChar = ""
        self.status = ""
        self.lines = []
        self.cursor = 0
        self.currentLine = 0
        self.selectStart = 0
        self.selectStartLine = 0
        self.selectEnd = 0
        self.selectEndLine = 0
        self.koreanMode = koreanMode
        self.multiLine = multi

    def SelectedText(self):
        if self.multiLine:
            temp = ""
            for i in range(len(self.lines)):
                if i < self.selectStartLine or i > self.selectEndLine:
                    continue
                else:
                    if i == self.selectStartLine and i != self.selectEndLine:
                        temp += self.lines[i][self.selectStart:]+'\n'
                    elif i != self.selectStartLine and i != self.selectEndLine:
                        temp += self.lines[i]+'\n'
                    elif i != self.selectStartLine and i == self.selectEndLine:
                        temp += self.lines[i][:self.selectEnd]
                    else:
                        temp = self.lines[self.currentLine][self.selectStart:self.selectEnd]
            return temp
        else:
            return self.lines[self.currentLine][self.selectStart:self.selectEnd]

    def Input(self, char):
        if self.selectStartLine != self.selectEndLine:
            lines = []
            for i, s in enumerate(self.lines):
                if i < self.selectStartLine or i > self.selectEndLine:
                    lines.append(s)
                elif i == self.selectStartLine:
                    if i == self.selectEndLine:
                        lines.append(self.lines[i][:self.selectStart] + self.lines[i][self.selectEnd:])
                    else:
                        lines.append(self.lines[i][:self.selectStart])
                elif i > self.selectStartLine and i < self.selectEndLine:
                    continue
                else:
                    lines.append(self.lines[i][self.selectEnd:])
            self.lines = lines
            self.currentLine = self.selectEndLine = self.selectStartLine
            self.cursor = self.selectEnd = self.selectStart
        elif self.selectStart != self.selectEnd:
            self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.lines[self.currentLine][self.selectEnd:]
            self.cursor = self.selectEnd = self.selectStart
        if self.koreanMode:
            self.processKoreanInput(char if char in UPPER_CASE else char.lower())
        else:
            if self.status != "":
                self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
                self.status = self.combineChar = ""
                self.cursor += 1
                self.selectStart = self.selectEnd = self.cursor
            self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + char + self.lines[self.currentLine][self.selectEnd:]
            self.cursor += 1
            self.selectStart = self.selectEnd = self.cursor

    def Delete(self, backspace=False):
        if self.selectStartLine != self.selectEndLine:
            temp = []
            for i, s in enumerate(self.lines):
                if i < self.selectStartLine or i > self.selectEndLine:
                    temp.append(s)
                else:
                    if i == self.selectStartLine and i != self.selectEndLine:
                        temp.append(s[:self.selectStart])
                    elif i != self.selectStartLine and i != self.selectEndLine:
                        continue
                    elif i != self.selectStartLine and i == self.selectEndLine:
                        temp[-1] += s[self.selectEnd:]
                    else:
                        temp.append(s[:self.selectStart]+s[self.selectEnd:])
            self.lines = temp
            self.currentLine = self.selectEndLine = self.selectStartLine
            self.cursor = self.selectEnd = self.selectStart
        elif self.selectStart != self.selectEnd:
            self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.lines[self.currentLine][self.selectEnd:]
            self.cursor = self.selectEnd = self.selectStart
        else:
            if backspace:
                if self.status != "":
                    self.status = self.status[:len(self.status)-1]
                    self.combineChar = self.combineChar[:len(self.combineChar)-1]
                else:
                    if self.selectStart > 0:
                        self.selectStart -= 1
                        self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.lines[self.currentLine][self.selectEnd:]
                        self.cursor = self.selectEnd = self.selectStart
                    elif self.currentLine > 0:
                        pos = len(self.lines[self.currentLine-1])
                        self.lines[self.currentLine-1] += self.lines[self.currentLine]
                        del self.lines[self.currentLine]
                        self.currentLine -= 1
                        self.selectStartLine = self.selectEndLine = self.currentLine
                        self.selectStart = self.selectEnd = self.cursor = pos
            else:
                if self.status != "":
                    self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
                    self.status = self.combineChar = ""
                    self.cursor += 1
                    self.selectStart = self.selectEnd = self.cursor
                else:
                    if self.cursor < len(self.lines[self.currentLine]):
                        self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.lines[self.currentLine][self.selectEnd+1:]
                    elif self.currentLine < len(self.lines) - 1:
                        self.lines[self.currentLine] += self.lines[self.currentLine+1]
                        del self.lines[self.currentLine+1]

    def LineHome(self, shift):
        if self.multiLine:
            atStart = True if self.currentLine == self.selectStartLine and self.cursor == self.selectStart else False
            if shift:
                if self.selectStartLine == self.selectEndLine:
                    if not atStart:
                        self.selectEnd = self.selectStart
                    self.selectStart = 0
                else:
                    if atStart:
                        self.selectStart = 0
                    else:
                        self.selectEnd = 0
                self.cursor = 0
            else:
                self.cursor = 0
                self.selectStartLine = self.selectEndLine = self.currentLine
                self.selectStart = self.selectEnd = self.cursor
        else:
            if shift:
                if self.selectStart == self.selectEnd:
                    if self.status != "":
                        self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
                        self.status = self.combineChar = ""
                        self.selectEnd += 1
                        self.cursor = self.selectStart = 0
                    else:
                        self.cursor = self.selectStart = 0
                else:
                    if self.cursor == self.selectEnd:
                        self.selectEnd = self.selectStart
                    self.cursor = self.selectStart = 0
            else:
                if self.status != "":
                    self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
                    self.status = self.combineChar = ""
                self.selectStart = self.selectEnd = self.cursor = 0

    def LineEnd(self, shift):
        if self.multiLine:
            atStart = True if self.currentLine == self.selectStartLine and self.cursor == self.selectStart else False
            if shift:
                if self.selectStartLine == self.selectEndLine:
                    if atStart:
                        self.selectStart = self.selectEnd
                    self.selectEnd = len(self.lines[self.currentLine])
                else:
                    if atStart:
                        self.selectStart = len(self.lines[self.currentLine])
                    else:
                        self.selectEnd = len(self.lines[self.currentLine])
                self.cursor = len(self.lines[self.currentLine])
            else:
                self.cursor = len(self.lines[self.currentLine])
                self.selectStartLine = self.selectEndLine = self.currentLine
                self.selectStart = self.selectEnd = self.cursor
        else:
            if shift:
                if self.selectStart == self.selectEnd:
                    if self.status != "":
                        self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
                        self.status = self.combineChar = ""
                        self.selectStart += 1
                    self.cursor = self.selectEnd = len(self.lines[self.currentLine])
                else:
                    if self.cursor == self.selectStart:
                        self.selectStart = self.selectEnd
                    self.cursor = self.selectEnd = len(self.lines[self.currentLine])
            else:
                if self.status != "":
                    self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
                    self.status = self.combineChar = ""
                self.selectStart = self.selectEnd = self.cursor = len(self.lines[self.currentLine])

    def MoveLeft(self, shift=False):
        atStart = True if self.currentLine == self.selectStartLine and self.cursor == self.selectStart else False
        if self.multiLine:
            if shift:
                if self.status != "":
                    self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
                    self.status = self.combineChar = ""
                    self.cursor += 1
                    self.selectEnd = self.cursor
                if self.cursor > 0:
                    self.cursor -= 1
                else:
                    if self.currentLine > 0:
                        self.currentLine -= 1
                        self.cursor = len(self.lines[self.currentLine])
                    else:
                        self.cursor = 0
                if atStart:
                    self.selectStartLine = self.currentLine
                    self.selectStart = self.cursor
                else:
                    self.selectEndLine = self.currentLine
                    self.selectEnd = self.cursor
            else:
                if self.selectStartLine == self.selectEndLine and self.selectStart == self.selectEnd:
                    if self.status == "":
                        if self.cursor > 0:
                            self.cursor = self.cursor - 1 
                        else:
                            if self.currentLine > 0:
                                self.currentLine -= 1
                                self.cursor = len(self.lines[self.currentLine])
                            else:
                                self.cursor = 0
                    else:
                        self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
                        self.status = self.combineChar = ""
                    self.selectStart = self.selectEnd = self.cursor
                    self.selectStartLine = self.selectEndLine = self.currentLine
                else:
                    self.cursor = self.selectEnd = self.selectStart
                    self.currentLine = self.selectEndLine = self.selectStartLine
        else:
            if shift:
                if self.selectStart == self.selectEnd:
                    if self.status == "":
                        self.cursor = max(0, self.cursor-1)
                        self.selectStart = self.cursor
                    else:
                        self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
                        self.status = self.combineChar = ""
                        self.selectEnd += 1
                else:
                    if self.cursor == self.selectStart:
                        self.cursor = max(0, self.cursor-1)
                        self.selectStart = self.cursor
                    else:
                        self.cursor = max(0, self.cursor-1)
                        self.selectEnd = self.cursor
            else:
                if self.selectStart == self.selectEnd:
                    if self.status == "":
                        self.cursor = max(0, self.cursor-1)
                    else:
                        self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
                        self.status = self.combineChar = ""
                    self.selectStart = self.selectEnd = self.cursor
                else:
                    self.cursor = self.selectEnd = self.selectStart
                    self.currentLine = self.selectEndLine = self.selectStartLine

    def MoveRight(self, shift=False):
        atEnd = True if self.currentLine == self.selectEndLine and self.cursor == self.selectEnd else False
        if self.multiLine:
            if shift:
                if self.status != "":
                    self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
                    self.status = self.combineChar = ""
                    self.selectStart += 1
                if self.cursor < len(self.lines[self.currentLine]):
                    self.cursor += 1
                else:
                    if self.currentLine < len(self.lines) - 1:
                        self.cursor = 0
                        self.currentLine += 1
                    else:
                        self.cursor = len(self.lines[self.currentLine])
                if atEnd:
                    self.selectEnd = self.cursor
                    self.selectEndLine = self.currentLine
                else:
                    self.selectStart = self.cursor
                    self.selectStartLine = self.currentLine
            else:
                if self.status == "":
                    if self.cursor < len(self.lines[self.currentLine]):
                        self.cursor += 1
                    else:
                        if self.currentLine < len(self.lines) - 1:
                            self.currentLine += 1
                            self.cursor = 0
                        else:
                            self.cursor = len(self.lines[self.currentLine])
                else:
                    self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
                    self.cursor += 1
                    self.status = self.combineChar = ""
                self.selectStart = self.selectEnd = self.cursor
                self.selectStartLine = self.selectEndLine = self.currentLine
        else:
            if shift:
                if self.selectStart == self.selectEnd:
                    if self.status != "":
                        self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
                        self.status = self.combineChar = ""
                        self.cursor += 1
                        self.selectStart = self.selectEnd = self.cursor
                    self.cursor = min(len(self.lines[self.currentLine]), self.cursor+1)
                    self.selectEnd = self.cursor
                else:
                    if self.cursor == self.selectStart:
                        self.cursor = min(len(self.lines[self.currentLine]), self.cursor+1)
                        self.selectStart = self.cursor
                    else:
                        self.cursor = min(len(self.lines[self.currentLine]), self.cursor+1)
                        self.selectEnd = self.cursor
            else:
                if self.selectStart == self.selectEnd:
                    if self.status != "":
                        self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
                        self.status = self.combineChar = ""
                    self.cursor = min(len(self.lines[self.currentLine]), self.cursor+1)
                    self.selectStart = self.selectEnd = self.cursor
                else:
                    self.cursor = self.selectStart = self.selectEnd

    def MoveUp(self, shift=False):
        atStart = True if self.currentLine == self.selectStartLine and self.cursor == self.selectStart else False
        if self.multiLine:
            if self.currentLine > 0 :
                self.currentLine -= 1
            self.cursor = min(self.cursor, len(self.lines[self.currentLine]))
            if shift:
                if atStart:
                    self.selectStartLine = self.currentLine
                    self.selectS = self.cursor
                else:
                    if self.currentLine < self.selectStartLine:
                        self.selectEndLine = self.selectStartLine
                        self.selectEnd = self.selectStart
                        self.selectStartLine = self.currentLine
                        self.selectStart = self.cursor
                    elif self.currentLine == self.selectStartLine:
                        if self.cursor < self.selectStart:
                            self.selectEndLine = self.selectStartLine
                            self.selectEnd = self.selectStart
                            self.selectStartLine = self.currentLine
                            self.selectStart = self.cursor
                        else:
                            self.selectEndLine = self.currentLine
                            self.selectEnd = self.cursor
                    else:
                        self.selectEndLine = self.currentLine
                        self.selectEnd = self.cursor
            else:
                self.selectStartLine = self.selectEndLine = self.currentLine
                self.selectStart = self.selectEnd = self.cursor

    def MoveDown(self, shift=False):
        atEnd = True if self.currentLine == self.selectEndLine and self.cursor == self.selectEnd else False
        if self.multiLine:
            if self.currentLine < len(self.lines) - 1:
                self.currentLine += 1
                self.cursor = min(self.cursor, len(self.lines[self.currentLine]))
            if shift:
                if atEnd:
                    self.selectEndLine = self.currentLine
                    self.selectEnd = self.cursor
                else:
                    if self.currentLine < self.selectEndLine:
                        self.selectStartLine = self.currentLine
                        self.cursor = min(self.curosr, len(self.lines[self.currentLine]))
                    elif self.currentLine == self.selectEndLine:
                        if self.cursor > self.selectEnd:
                            self.selectStart = self.selectEnd
                            self.selectEnd = self.cursor
                        self.selectStartLine = self.currentLine
                    else:
                        self.selectStartLine = self.selectEndLine
                        self.selectStart = self.selectEnd
                        self.selectEndLine = self.currentLine
                        self.selectEnd = self.cursor
            else:
                self.selectStartLine = self.selectEndLine = self.currentLine
                self.selectStart = self.selectEnd = self.cursor

    def LineFeed(self):
        if not self.multiLine:
            return
        if self.selectStartLine != self.selectEndLine:
            temp = []
            for i, s in enumerate(self.lines):
                if i < self.selectStartLine or i > self.selectEndLine:
                    temp.append(s)
                else:
                    if i == self.selectStartLine and i != self.selectEndLine:
                        temp.append(s[:self.selectStart])
                    elif i != self.selectStartLine and i != self.selectEndLine:
                        continue
                    elif i != self.selectStartLine and i == self.selectEndLine:
                        temp[-1] += s[self.selectEnd:]
                    else:
                        temp.append(s[:self.selectStart]+s[self.selectEnd:])
            self.lines = temp
            self.currentLine = self.selectEndLine = self.selectStartLine
            self.cursor = self.selectEnd = self.selectStart
        elif self.selectStart != self.selectEnd:
            self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.lines[self.currentLine][self.selectEnd:]
            self.cursor = self.selectEnd = self.selectStart

        if self.status != "":
            self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
            self.status = self.combineChar = ""
            self.cursor += 1
            self.selectStart = self.selectEnd = self.cursor
        newLine = self.lines[self.currentLine][self.cursor:]
        self.lines[self.currentLine] = self.lines[self.currentLine][:self.cursor]
        self.lines.insert(self.currentLine+1, newLine)
        self.currentLine += 1
        self.selectStartLine = self.selectEndLine = self.currentLine
        self.selectStart = self.selectEnd = self.cursor = 0
        

    def SelectAll(self):
        if self.status != "":
            self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
            self.status = self.combineChar = ""
        if self.multiLine:
            self.selectStartLine = self.selectStart = 0
            self.selectEndLine = self.currentLine = len(self.lines) - 1
            self.selectEnd = self.cursor = len(self.lines[self.currentLine])
        else:
            self.selectStart = 0
            self.cursor = self.selectEnd = len(self.lines[self.currentLine])

    def Paste(self, text):
        if self.status != "":
            self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
            self.status = self.combineChar = ""
            self.cursor += 1
            self.selectStart = self.selectEnd = self.cursor
        if self.selectStartLine != self.selectEndLine:
            temp = []
            for i, s in enumerate(self.lines):
                if i < self.selectStartLine or i > self.selectEndLine:
                    temp.append(s)
                else:
                    if i == self.selectStartLine and i != self.selectEndLine:
                        temp.append(s[:self.selectStart])
                    elif i != self.selectStartLine and i != self.selectEndLine:
                        continue
                    elif i != self.selectStartLine and i == self.selectEndLine:
                        temp[-1] += s[self.selectEnd:]
                    else:
                        temp.append(s[:self.selectStart]+s[self.selectEnd:])
            self.lines = temp
            self.currentLine = self.selectEndLine = self.selectStartLine
            self.cursor = self.selectEnd = self.selectStart
        elif self.selectStart != self.selectEnd:
            self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.lines[self.currentLine][self.selectEnd:]
            self.cursor = self.selectEnd = self.selectStart
        if self.multiLine:
            temp = text.split('\n')
            leftText = self.lines[self.currentLine][:self.cursor]
            rightText = self.lines[self.currentLine][self.cursor:]
            for i in range(len(temp)):
                if i == 0:
                    if len(temp) > 1:
                        self.lines[self.currentLine] = leftText + temp[i]
                    else:
                        self.lines[self.currentLine] = leftText + temp[i] + rightText
                        self.cursor += len(temp[i])
                elif i > 0 and i < len(temp) - 2:
                    self.lines.insert(self.currentLine + 1, temp[i])
                    self.currentLine += 1
                elif i == len(temp) - 1:
                    self.lines.insert(self.currentLine + 1, temp[i])
                    self.currentLine += 1
                    self.cursor = len(self.lines[self.currentLine])
                    self.lines[self.currentLine] += rightText
        else:
            self.lines[self.currentLine] = self.lines[self.currentLine][:self.cursor] + text + self.lines[self.currentLine][self.cursor:]
            self.cursor = self.selectStart + len(text)
            self.selectStart = self.selectEnd = self.cursor

    def GetMode(self):
        return self.koreanMode

    def SetMode(self, mode):
        if self.status != "":
            self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
            self.status = self.combineChar = ""
            self.cursor += 1
            self.selectStart = self.selectEnd = self.cursor
        self.koreanMode = mode

    def SetText(self, text, multi=False):
        self.lines = text.split('\n')
        self.status = self.combineChar = ""
        self.multiLine = multi
        if multi:
            self.selectStart = self.selectStartLine = 0
            self.currentLine = self.selectEndLine = len(self.lines) - 1
            self.selectEnd = self.cursor = len(self.lines[-1])
        else:
            self.selectStart = self.selectStartLine = self.selectEndLine = self.currentLine = 0
            self.selectEnd = self.cursor = len(self.lines[0])

    def GetText(self):
        text = ""
        cnt = len(self.lines)
        if self.multiLine:
            for i in range(cnt):
                if i == self.currentLine and self.status != "":
                    text += self.lines[i][:self.cursor] + self.combine() + self.lines[i][self.cursor:]
                else:
                    text += self.lines[i]
                if i < cnt - 1:
                    text += '\n'
        else:
            if self.status != "":
                text = self.lines[0][:self.cursor] + self.combine() + self.lines[0][self.cursor:]
            else:
                text = self.lines[0]
        return text

    def processKoreanInput(self, char):
        cType = self.getType(char)
        if cType == 'C':
            self.processConsonant(char)
        elif cType == 'V':
            self.processVowel(char)
        else:
            if self.status != "":
                self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
                self.status = self.combineChar = ""
                self.cursor += 1
                self.selectStart = self.selectEnd = self.cursor
            self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + char + self.lines[self.currentLine][self.selectEnd:]
            self.cursor += 1
            self.selectStart = self.selectEnd = self.cursor

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
                self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
                self.cursor += 1
                self.selectStart = self.selectEnd = self.cursor
                self.status = "C"
                self.combineChar = char
        elif self.status in {"CC", "V", "VV"}:
            self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
            self.cursor += 1
            self.selectStart = self.selectEnd = self.cursor
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
                self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
                self.cursor += 1
                self.selectStart = self.selectEnd = self.cursor
                self.status = "C"
                self.combineChar = char
        elif self.status in {"CVCC"}:
            self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
            self.cursor += 1
            self.selectStart = self.selectEnd = self.cursor
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
                self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
                self.cursor += 1
                self.selectStart = self.selectEnd = self.cursor
                self.status = "V"
                self.combineChar = char
        elif self.status == "CC":
            second_char = self.combineChar[1]
            self.combineChar = self.combineChar[0]
            self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
            self.cursor += 1
            self.selectStart = self.selectEnd = self.cursor
            self.status = "V"
            self.combineChar = char
        elif self.status == "CV":
            dc = self.combineChar[-1] + char
            if dc in PHOENMES:
                self.status += "V"
                self.combineChar += char
            else:
                self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
                self.cursor += 1
                self.selectStart = self.selectEnd = self.cursor
                self.status = "V"
                self.combineChar = char
        elif self.status in {"VV", "CVV"}:
            self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
            self.cursor += 1
            self.selectStart = self.selectEnd = self.cursor
            self.status = "V"
            self.combineChar = char
        elif self.status in {"CVC", "CVCC", "CVVC", "CVVCC"}:
            last_char = self.combineChar[-1]
            self.combineChar = self.combineChar[:len(self.combineChar)-1]
            self.status = self.status[:len(self.status)-1]
            self.lines[self.currentLine] = self.lines[self.currentLine][:self.selectStart] + self.combine() + self.lines[self.currentLine][self.selectEnd:]
            self.cursor += 1
            self.selectStart = self.selectEnd = self.cursor
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
            return chr(BASE_CODE[1] + cho * 588 + jung * 28 + jong)
        elif self.status == "CVVCC":
            cho = CHOSEONG.index(self.combineChar[0])
            jung = JUNGSEONG.index(self.combineChar[1:3])
            jong = JONGSEONG.index(self.combineChar[3:5])
            return chr(BASE_CODE[1] + cho * 588 + jung * 28 + jong)
        return ""
