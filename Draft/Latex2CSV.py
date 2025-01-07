# -*- coding: utf-8 -*-
# @Time     : 2024-12-23-17:48
# @Author   : Sum3 TEO
# @E-mail   : rui3zhang@163

import pandas as pd
import re

# LaTeX 表格的内容
latex_table = r"""
% Please add the following required packages to your document preamble:
% \usepackage{multirow}
\begin{table*}[htbp!]
\caption{Experiments of Set 2a 1}
\resizebox{\textwidth}{!}{%
% \begin{table}[]
\begin{tabular}{lccccccccccccccc}
\hline
\multicolumn{1}{c}{\multirow{2}{*}{Instance}} &
  \multirow{2}{*}{$|V_{od}|$} &
  \multirow{2}{*}{$|V_{c}|$} &
  \multirow{2}{*}{$|V_{s}|$} &
   &
  \multicolumn{4}{c}{Gurobi Solver} &
   &
  \multicolumn{3}{c}{ALNS/TD} &
   &
  \multirow{2}{*}{Gap(Best) \%} &
  \multirow{2}{*}{\makecell{Gap\\(Average)} \%} \\ \cline{6-9} \cline{11-13}
\multicolumn{1}{c}{} &    &    &   &  & UB      & LB      & Gap(\%) & \makecell{CPU\\ time(s)} &  & \makecell{Obj\\(Best)} & \makecell{Obj\\(Average)} & \makecell{Average\\ CPU time(s)} &  &          &          \\ \hline
E-n22-k4-s6-17       & 7  & 21 & 2 &  & 3836.37 & 3660.52 & 4.58\%  & 3600        &  & 3836.37   & 3836.37      & 15.69                    &  & 0.00\%   & 0.00\%   \\
E-n22-k4-s8-14       & 7  & 21 & 2 &  & 3355.03 & 2875.59 & 14.29\% & 3600        &  & 3342.67   & 3342.67      & 10.22                    &  & -0.37\%  & -0.37\%  \\
E-n22-k4-s9-19       & 7  & 21 & 2 &  & 3775.86 & 2568.45 & 31.98\% & 3600        &  & 3744.78   & 3744.78      & 1.43                     &  & -0.82\%  & -0.82\%  \\
E-n22-k4-s10-14      & 7  & 21 & 2 &  & 3219.84 & 2358.69 & 26.75\% & 3600        &  & 3203.27   & 3203.32      & 9.61                     &  & -0.51\%  & -0.51\%  \\
E-n22-k4-s11-12      & 7  & 21 & 2 &  & 4375.71 & 1860.81 & 57.47\% & 3600        &  & 3871.76   & 3886.65      & 18.80                    &  & -11.52\% & -11.18\% \\
E-n22-k4-s12-16      & 7  & 21 & 2 &  & 3523.91 & 2362.91 & 32.95\% & 3600        &  & 3418.83   & 3418.83      & 5.02                     &  & -2.98\%  & -2.98\%  \\
E-n33-k4-s1-9        & 10 & 32 & 2 &  & —       & —       & —       & 3600        &  & 5782.20   & 5846.69      & 34.15                    &  & —        & —        \\
E-n33-k4-s2-13       & 10 & 32 & 2 &  & 6232.40 & 3770.01 & 39.51\% & 3600        &  & 5769.59   & 5798.33      & 50.87                    &  & -7.43\%  & -6.96\%  \\
E-n33-k4-s3-17       & 10 & 32 & 2 &  & —       & —       & —       & 3600        &  & 6165.98   & 6179.29      & 20.74                    &  & —        & —        \\
E-n33-k4-s4-5        & 10 & 32 & 2 &  & —       & —       & —       & 3600        &  & 5782.20   & 5846.69      & 34.15                    &  & —        & —        \\
E-n33-k4-s7-25       & 10 & 32 & 2 &  & —       & —       & —       & 3600        &  & 5942.69   & 6006.78      & 33.11                    &  & —        & —        \\
E-n33-k4-s14-22      & 10 & 32 & 2 &  & 6638.46 & 5253.88 & 20.86\% & 3600        &  & 6395.39   & 6395.39      & 27.69                    &  & -3.66\%  & -3.66\%  \\ \hline
\end{tabular}
% \end{table}
}
\label{ex:set2a grb}
\end{table*}
"""

# 清理 LaTeX 表格语法，提取表格数据
table_data = []
for line in latex_table.split("\\\\"):
    # 删除多余的 LaTeX 命令
    line = re.sub(r"\\.*?\{.*?\}", "", line)
    line = line.strip()
    if line:
        table_data.append(line.split("&"))

# 将数据转为 DataFrame
df = pd.DataFrame(table_data)

print(df)