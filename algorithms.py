import random
from collections import defaultdict, deque

class PageReplacementBase: #初始化
    def __init__(self, frames):
        self.frames = frames
        self.memory = []
        self.reference_bits = {}
        self.dirty_bits = {}
        self.interrupts = 0
        self.page_faults = 0
        self.disk_writes = 0

    def access_page(self, page, is_write=False): #框架
        raise NotImplementedError #DoNothing

    def get_stats(self): #回傳結果
        return self.page_faults, self.interrupts, self.disk_writes


# FIFO
class FIFO(PageReplacementBase):
    def __init__(self, frames):
        super().__init__(frames)
        self.queue = [] #queue紀錄進入順序

    def access_page(self, page, is_write=False):
        if page in self.memory:
            if is_write:
                self.dirty_bits[page] = True #標記為髒頁
            return

        self.page_faults += 1
        self.interrupts += 1

        if len(self.memory) < self.frames: #還有空位
            self.memory.append(page)
            self.queue.append(page)
        else:
            victim = self.queue.pop(0) #丟掉最早的
            if self.dirty_bits.get(victim, False):
                self.disk_writes += 1
            self.memory.remove(victim)
            self.memory.append(page)
            self.queue.append(page)

        self.dirty_bits[page] = is_write #更新髒頁狀態


# Optimal
class Optimal(PageReplacementBase):
    def __init__(self, frames, ref_string): 
        super().__init__(frames) 
        self.ref_string = ref_string 
        self.pointer = 0
        self.future_positions = defaultdict(deque) #紀錄每個page未來會在哪些位置被存取
        for i, page in enumerate(ref_string):
            self.future_positions[page].append(i) 

    def access_page(self, page, is_write=False): 
        if self.future_positions[page]:
            self.future_positions[page].popleft() #移除當前位置

        if page in self.memory:
            if is_write:
                self.dirty_bits[page] = True 
            self.pointer += 1
            return

        self.page_faults += 1
        self.interrupts += 1

        if len(self.memory) < self.frames:
            self.memory.append(page) 
        else:
            victim = None
            farthest = -1
            for p in self.memory:
                if not self.future_positions[p]: #不會再用到
                    victim = p 
                    break
                next_use = self.future_positions[p][0] #下一次使用位置
                if next_use > farthest: #找最遠的
                    farthest = next_use 
                    victim = p
            if self.dirty_bits.get(victim, False): #髒頁寫回
                self.disk_writes += 1
            self.memory.remove(victim)
            self.memory.append(page)

        self.dirty_bits[page] = is_write
        self.pointer += 1


# Additional Reference Bits (ARB)
class ARB(PageReplacementBase):
    def __init__(self, frames):
        super().__init__(frames)
        self.reference_bits = {}

    def periodic_shift(self):
        for page in self.memory:
            self.reference_bits[page] >>= 1 #右移一位

    def access_page(self, page, is_write=False):
        if page in self.memory:
            self.reference_bits[page] |= 0b10000000 #設最高位元
            if is_write:
                self.dirty_bits[page] = True
            return

        self.page_faults += 1
        self.interrupts += 1

        if len(self.memory) >= self.frames: #沒有空位才需要置換；新頁統一在下方加入
            victim = min(self.memory, key=lambda p: self.reference_bits[p]) #找參考位元最小的
            if self.dirty_bits.get(victim, False):
                self.disk_writes += 1
            self.memory.remove(victim)

        self.memory.append(page)
        self.reference_bits[page] = 0b10000000 #新頁最高位元設1
        self.dirty_bits[page] = is_write


# Custom Dirty-Aware ARB
class CustomAlgorithm(PageReplacementBase):
    def __init__(self, frames):
        super().__init__(frames)
        self.reference_bits = {}

    def periodic_shift(self):
        for page in self.memory:
            self.reference_bits[page] >>= 1 #右移一位

    def access_page(self, page, is_write=False):
        if page in self.memory:
            self.reference_bits[page] |= 0b10000000 #設最高位元
            if is_write:
                self.dirty_bits[page] = True
            return

        self.page_faults += 1
        self.interrupts += 1

        if len(self.memory) >= self.frames: #沒有空位才需要置換；新頁統一在下方加入
            clean_pages = [p for p in self.memory if not self.dirty_bits.get(p, False)] #找乾淨頁
            if clean_pages:
                victim = min(clean_pages, key=lambda p: self.reference_bits[p]) #乾淨頁中找參考位元最小的
            else:
                victim = min(self.memory, key=lambda p: self.reference_bits[p]) #全找參考位元最小的
                if self.dirty_bits.get(victim, False): 
                    self.disk_writes += 1
            self.memory.remove(victim)

        self.memory.append(page)
        self.reference_bits[page] = 0b10000000 
        self.dirty_bits[page] = is_write