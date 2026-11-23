"""
第 1 周 · 语言差异点 10：切片
================================================================
【对应知识点】文档第 1 周「语言差异点」第 10 项：切片

【周次学习要点】
  - 切片语法 seq[start:stop:step]，左闭右开（含 start 不含 stop），step 为步长。
  - 负数索引从末尾数；[::-1] 是反转序列的惯用写法。
  - 切片**不越界**：超出范围会自动截断，不抛 IndexError（与单个索引 nums[100] 不同）。

【易忽略细节】
  1. 切片返回的是**新对象**，但元素是浅拷贝：嵌套列表的内层对象仍共享引用（见下方演示，
     与 pitfalls/extra_gotchas.py 的浅拷贝坑呼应）。
  2. step 为负数时 start/stop 的方向也会反过来，[::-1] 省略两端即从尾到头全取。
  3. slice 对象可以复用：s = slice(1, 5, 2); seq[s] 等价于 seq[1:5:2]。

【示例用途】可运行：`python week01/language_features/10_slicing.py`
"""
from __future__ import annotations


def main() -> None:
    print("=== 10 切片 ===")
    nums = list(range(10))

    print(f"  原列表            : {nums}")
    print(f"  [2:8]             : {nums[2:8]}")
    print(f"  [2:8:2] 步长 2    : {nums[2:8:2]}")
    print(f"  [-3:] 最后 3 个   : {nums[-3:]}")
    print(f"  [::-1] 反转       : {nums[::-1]}")
    print(f"  [100:200] 不越界  : {nums[100:200]} —— 返回空列表，不报错")

    s = slice(1, 5, 2)
    print(f"  slice 对象复用    : {nums[s]}")

    copy = nums[:]
    copy[0] = 99
    print(f"  切片是新对象      : nums[0]={nums[0]}（原列表不受影响）")

    nested = [[1], [2], [3]]
    shallow = nested[:]
    shallow[0].append(999)
    print(f"  但元素是浅拷贝    : {nested} —— 内层列表被改动了（共享引用）")


if __name__ == "__main__":
    main()
