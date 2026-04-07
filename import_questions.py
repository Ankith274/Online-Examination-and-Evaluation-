import re
import json
from app import app
from models import db, Subject, Exam, Question, User

text_data = """
perating Systems MCQs

1. What is an Operating System?
A) A programming language
B) System software
C) Text editor
D) Hardware
Answer: B

2. Which of the following is the main function of an OS?
A) Cooking food
B) Managing computer resources
C) Drawing images only
D) Playing songs only
Answer: B

3. Which is not an operating system?
A) Linux
B) Windows
C) Oracle
D) macOS
Answer: C

4. Which OS allows multiple users to use the system at the same time?
A) Single-user OS
B) Multi-user OS
C) Batch OS
D) Embedded OS
Answer: B

5. Which scheduling algorithm works on First Come First Serve basis?
A) FCFS
B) SJF
C) Round Robin
D) Priority
Answer: A

6. Which scheduling algorithm gives minimum average waiting time in ideal case?
A) FCFS
B) SJF
C) FIFO
D) LIFO
Answer: B

7. In Round Robin scheduling, CPU is assigned for a fixed time called:
A) Slot
B) Quantum
C) Share
D) Window
Answer: B

8. A process is:
A) Program in execution
B) Program in memory only
C) Software bug
D) Hardware unit
Answer: A

9. PCB stands for:
A) Process Control Block
B) Program Control Base
C) Processor Cache Block
D) Process Common Base
Answer: A

10. Which memory is fastest?
A) RAM
B) Cache
C) Hard disk
D) ROM
Answer: B

11. Main memory is also called:
A) Secondary memory
B) Primary memory
C) Virtual memory
D) Cache memory
Answer: B

12. Which of the following is secondary storage?
A) RAM
B) Register
C) Hard disk
D) Cache
Answer: C

13. Deadlock occurs when:
A) Processes are sleeping
B) Processes wait forever for resources
C) CPU is idle
D) Memory is free
Answer: B

14. Which is a necessary condition for deadlock?
A) Mutual exclusion
B) Compilation
C) Interpretation
D) Encryption
Answer: A

15. Thrashing occurs when:
A) CPU works very fast
B) System spends more time swapping than executing
C) Keyboard fails
D) Printer stops
Answer: B

16. Virtual memory is:
A) Real physical memory
B) Memory on disk used as extension of RAM
C) Cache memory
D) ROM memory
Answer: B

17. Paging is used for:
A) Process termination
B) Memory management
C) CPU scheduling
D) File compression
Answer: B

18. Page fault occurs when:
A) CPU crashes
B) Required page is not in memory
C) Disk is full
D) File is deleted
Answer: B

19. Which of the following is not a CPU scheduling algorithm?
A) Round Robin
B) SJF
C) Priority
D) Paging
Answer: D

20. Semaphore is used for:
A) File naming
B) Process synchronization
C) Disk formatting
D) Program editing
Answer: B

21. The command interpreter in OS is called:
A) Shell
B) Kernel
C) Compiler
D) Loader
Answer: A

22. Kernel is:
A) Core part of operating system
B) Type of file
C) Application software
D) Database
Answer: A

23. Which OS is open source?
A) Windows
B) Linux
C) iOS
D) MS DOS only
Answer: B

24. Context switching means:
A) Changing program language
B) Saving one process and loading another
C) Installing software
D) Deleting process
Answer: B

25. Which one is a real-time operating system?
A) DOS
B) UNIX
C) VxWorks
D) Windows XP
Answer: C

26. File system helps in:
A) CPU scheduling
B) Organizing files on storage
C) Drawing graphics
D) Sending emails
Answer: B

27. Fragmentation in memory can be:
A) Internal and external
B) Input and output
C) Static and dynamic only
D) Manual and automatic
Answer: A

28. Which one is not a process state?
A) Ready
B) Running
C) Waiting
D) Compiled
Answer: D

29. Dispatcher is used for:
A) Sending emails
B) Giving CPU to selected process
C) Memory allocation only
D) File deletion
Answer: B

30. Starvation means:
A) CPU overload
B) Process waits indefinitely
C) Disk crash
D) User logout
Answer: B

31. Which is responsible for booting the computer?
A) Compiler
B) Bootstrap loader
C) Text editor
D) Browser
Answer: B

32. Spooling is used in:
A) Printing
B) Gaming
C) Browsing
D) Compiling
Answer: A

33. Multitasking means:
A) Running one task only
B) Running multiple tasks apparently at same time
C) No task execution
D) Only background task
Answer: B

34. A thread is:
A) Lightweight process
B) Heavy disk
C) Type of file
D) Memory block
Answer: A

35. Which one is non-preemptive scheduling?
A) Round Robin
B) FCFS
C) Priority preemptive
D) SRTF
Answer: B

36. The brain of operating system is:
A) Shell
B) Kernel
C) RAM
D) File
Answer: B

37. Which command is used to create directory in Linux?
A) cd
B) rm
C) mkdir
D) rmdir
Answer: C

38. Which command is used to list files in Linux?
A) list
B) ls
C) show
D) dirr
Answer: B

39. Which of the following is a GUI based OS?
A) Windows
B) DOS
C) Shell script
D) BIOS
Answer: A

40. Resource allocation graph is used for:
A) File editing
B) Deadlock detection
C) CPU manufacturing
D) Program loading
Answer: B

41. Which of these is a synchronization problem?
A) Producer-consumer
B) Sorting
C) Searching
D) Merging
Answer: A

42. The smallest unit of execution is:
A) Program
B) Thread
C) File
D) Disk
Answer: B

43. A shell script is used for:
A) Automation of commands
B) Hardware repair
C) Virus creation
D) File compression only
Answer: A

44. Which memory is volatile?
A) ROM
B) Hard disk
C) RAM
D) CD-ROM
Answer: C

45. Which one is a mobile operating system?
A) Android
B) Oracle
C) Python
D) Ubuntu compiler
Answer: A

46. Inter-process communication means:
A) Communication between processors
B) Communication between processes
C) Communication between files
D) Communication between disks
Answer: B

47. Banker’s algorithm is used for:
A) CPU scheduling
B) Deadlock avoidance
C) Page replacement
D) File allocation
Answer: B

48. Which page replacement algorithm replaces the oldest page?
A) FIFO
B) LRU
C) Optimal
D) SJF
Answer: A

49. LRU stands for:
A) Last Recently Used
B) Least Recently Used
C) Long Random Unit
D) Least Required Unit
Answer: B

50. Which one is the correct sequence of booting?
A) OS → BIOS → Bootloader
B) BIOS → Bootloader → OS
C) Bootloader → BIOS → OS
D) OS → Bootloader → BIOS
Answer: B

Python MCQs

51. Python is a:
A) Low-level language
B) High-level language
C) Assembly language
D) Machine language
Answer: B

52. Python is:
A) Compiled only
B) Interpreted language
C) Hardware
D) OS
Answer: B

53. Who developed Python?
A) Dennis Ritchie
B) Guido van Rossum
C) James Gosling
D) Bjarne Stroustrup
Answer: B

54. Which symbol is used for comments in Python?
A) //
B) #
C) /* */
D) --
Answer: B

55. Which function is used to display output?
A) input()
B) display()
C) print()
D) show()
Answer: C

56. Which function is used to take input?
A) read()
B) scanf()
C) input()
D) get()
Answer: C

57. Python supports:
A) Object-oriented programming
B) Functional programming
C) Procedural programming
D) All of these
Answer: D

58. Which data type is immutable?
A) List
B) Dictionary
C) Set
D) Tuple
Answer: D

59. Which bracket is used for list?
A) {}
B) ()
C) []
D) <>
Answer: C

60. Which bracket is used for tuple?
A) ()
B) []
C) {}
D) //
Answer: A

61. Dictionary stores data in:
A) Ordered pairs of key-value
B) Single values only
C) Random symbols only
D) Function form
Answer: A

62. Which keyword is used to define a function?
A) function
B) define
C) def
D) fun
Answer: C

63. Which keyword is used for loop?
A) repeat
B) for
C) loop
D) iterate
Answer: B

64. Which keyword is used for conditional statement?
A) choose
B) if
C) when
D) select
Answer: B

65. Which operator is used for exponentiation?
A) ^
B) **
C) //
D) %%
Answer: B

66. len() is used to:
A) Calculate length
B) Add elements
C) Convert to integer
D) Print data
Answer: A

67. Which of the following is correct variable name?
A) 2name
B) my-name
C) my_name
D) class
Answer: C

68. Python is case:
A) Not sensitive
B) Sensitive
C) Numeric
D) Object only
Answer: B

69. Which of these is a valid Python data type?
A) int
B) float
C) str
D) All of these
Answer: D

70. The output of type(10) is:
A) float
B) str
C) int
D) bool
Answer: C

71. Which method adds an item to list?
A) add()
B) append()
C) insertitem()
D) push()
Answer: B

72. Which method removes an item from dictionary by key?
A) delete()
B) pop()
C) remove()
D) clearone()
Answer: B

73. Which keyword is used to create class?
A) define
B) class
C) object
D) struct
Answer: B

74. Which function converts string to integer?
A) str()
B) float()
C) int()
D) bool()
Answer: C

75. Which operator is used for floor division?
A) /
B) //
C) %
D) **
Answer: B

76. Which one gives remainder?
A) /
B) //
C) %
D) *
Answer: C

77. True and False belong to:
A) str
B) float
C) bool
D) list
Answer: C

78. Which statement stops a loop completely?
A) skip
B) break
C) pass
D) continue
Answer: B

79. Which statement skips current iteration?
A) pass
B) break
C) continue
D) stop
Answer: C

80. pass statement means:
A) End program
B) Do nothing
C) Skip forever
D) Print output
Answer: B

81. Which module is used for mathematical functions?
A) random
B) math
C) os
D) sys
Answer: B

82. Which module is used for random numbers?
A) random
B) math
C) time
D) file
Answer: A

83. Which file extension is used for Python files?
A) .pt
B) .py
C) .python
D) .pyt
Answer: B

84. What is the output of 5 > 3?
A) 5
B) 3
C) True
D) False
Answer: C

85. Which method converts text to lowercase?
A) lower()
B) small()
C) down()
D) case()
Answer: A

86. Which method converts text to uppercase?
A) upper()
B) caps()
C) big()
D) top()
Answer: A

87. What is slicing in Python?
A) Breaking program
B) Accessing part of sequence
C) Deleting variable
D) Running loop
Answer: B

88. range(5) gives:
A) 1 to 5
B) 0 to 4
C) 0 to 5
D) 1 to 4
Answer: B

89. Which keyword is used to import module?
A) include
B) using
C) import
D) load
Answer: C

90. Which of the following is a Python framework for web development?
A) Flask
B) NumPy
C) Pandas
D) TensorFlow
Answer: A

91. Exception handling keyword is:
A) catch only
B) try
C) check
D) error
Answer: B

92. Which block is executed if exception occurs?
A) else
B) finally
C) except
D) pass
Answer: C

93. Which block always executes?
A) except
B) try
C) finally
D) else
Answer: C

94. Python supports inheritance?
A) Yes
B) No
C) Only in C
D) Only with libraries
Answer: A

95. Which method is constructor in Python?
A) start
B) init
C) create
D) begin
Answer: B

96. Lambda is used for:
A) Multi-line function
B) Anonymous function
C) Class creation
D) File opening
Answer: B

97. Which function opens a file?
A) file()
B) open()
C) fopen()
D) create()
Answer: B

98. Which mode is used to read file?
A) w
B) a
C) r
D) x
Answer: C

99. Which mode is used to append file?
A) a
B) r
C) w
D) x
Answer: A

100. Which collection does not allow duplicate values?
A) list
B) tuple
C) set
D) string
Answer: C

Machine Learning MCQs

101. Machine Learning is a branch of:
A) Biology
B) Artificial Intelligence
C) Physics
D) Networking
Answer: B

102. ML system learns from:
A) Keyboard only
B) Data
C) Monitor
D) Printer
Answer: B

103. Which is a type of machine learning?
A) Supervised learning
B) Unsupervised learning
C) Reinforcement learning
D) All of these
Answer: D

104. In supervised learning, data has:
A) No labels
B) Labels
C) Images only
D) Audio only
Answer: B

105. In unsupervised learning, data has:
A) Labels
B) No labels
C) Only numbers
D) Only strings
Answer: B

106. Which of the following is a supervised learning algorithm?
A) K-Means
B) Linear Regression
C) PCA
D) Apriori
Answer: B

107. Which of the following is used for classification?
A) Logistic Regression
B) Linear Regression
C) PCA
D) K-Means only
Answer: A

108. Which algorithm is used for clustering?
A) K-Means
B) Decision Tree
C) Linear Regression
D) Naive Bayes
Answer: A

109. Which algorithm is used for regression?
A) Linear Regression
B) KNN classifier
C) K-Means
D) Apriori
Answer: A

110. Overfitting means:
A) Model performs well on training and test equally
B) Model memorizes training data and performs poorly on new data
C) Model has no data
D) Model runs slowly
Answer: B

111. Underfitting means:
A) Model is too simple
B) Model is too complex
C) Model is perfect
D) Model has extra memory
Answer: A

112. Training data is used to:
A) Test final model
B) Train model
C) Delete model
D) Compress model
Answer: B

113. Test data is used to:
A) Train model
B) Evaluate model
C) Store model
D) Normalize data
Answer: B

114. Accuracy is mainly used in:
A) Classification
B) Clustering
C) Data cleaning
D) Compression
Answer: A

115. MAE stands for:
A) Mean Absolute Error
B) Maximum Absolute Error
C) Mean Average Estimation
D) Model Accuracy Error
Answer: A

116. MSE stands for:
A) Mean Squared Error
B) Model Standard Error
C) Mean Scaled Evaluation
D) Maximum Squared Error
Answer: A

117. RMSE stands for:
A) Root Mean Squared Error
B) Relative Mean Square Error
C) Root Model Standard Error
D) Range Mean Square Error
Answer: A

118. Which is an ensemble algorithm?
A) Random Forest
B) Linear Regression
C) K-Means
D) PCA
Answer: A

119. Decision Tree can be used for:
A) Classification
B) Regression
C) Both
D) None
Answer: C

120. Random Forest is made of many:
A) Neural networks
B) Trees
C) Clusters
D) Tables
Answer: B

121. KNN stands for:
A) Known Nearest Node
B) K-Nearest Neighbors
C) Key Network Node
D) K-Normal Neuron
Answer: B

122. KNN is based on:
A) Distance
B) Sorting
C) Encryption
D) Compilation
Answer: A

123. Logistic Regression is mainly used for:
A) Classification
B) Clustering
C) Compression
D) Regression only always
Answer: A

124. Which algorithm is based on Bayes theorem?
A) Naive Bayes
B) KNN
C) K-Means
D) Random Forest
Answer: A

125. SVM stands for:
A) Support Vector Machine
B) Simple Vector Method
C) Signal Vector Machine
D) Support Variable Method
Answer: A

126. Which is used to reduce dimensions?
A) PCA
B) KNN
C) SVM
D) Naive Bayes
Answer: A

127. PCA stands for:
A) Principal Component Analysis
B) Primary Component Algorithm
C) Partial Classification Analysis
D) Program Component Analysis
Answer: A

128. Feature means:
A) Output label
B) Input variable
C) Error rate
D) Final score
Answer: B

129. Label means:
A) Target output
B) Input variable
C) Missing data
D) Noise
Answer: A

130. Confusion matrix is used in:
A) Classification
B) Clustering
C) Regression
D) PCA
Answer: A

131. Precision tells:
A) Total errors
B) Correct positive predictions over predicted positives
C) Total samples
D) Total negatives
Answer: B

132. Recall tells:
A) Correct positive predictions over actual positives
B) Correct negatives only
C) Wrong predictions only
D) Missing values only
Answer: A

133. F1-score is:
A) Harmonic mean of precision and recall
B) Arithmetic mean of error
C) Geometric mean of labels
D) Mean of training data
Answer: A

134. Cross-validation is used to:
A) Delete data
B) Evaluate model robustness
C) Increase file size
D) Draw graph only
Answer: B

135. Hyperparameters are:
A) Learned from training automatically always
B) Set before training
C) Output labels
D) Missing values
Answer: B

136. Learning rate is important in:
A) Gradient-based models
B) File handling
C) Operating system
D) Sorting only
Answer: A

137. Gradient descent is used for:
A) Optimization
B) Compression
C) Encryption
D) Clustering only
Answer: A

138. Neural network is inspired by:
A) Brain
B) Printer
C) Disk
D) Compiler
Answer: A

139. Deep learning uses:
A) Single layer only
B) Multiple layers
C) No layers
D) File layers
Answer: B

140. Which library is popular for ML in Python?
A) scikit-learn
B) turtle
C) pygame
D) tkinter only
Answer: A

141. Which library is popular for deep learning?
A) TensorFlow
B) NumPy only
C) pickle
D) os
Answer: A

142. Bias in ML refers to:
A) Systematic error
B) Random file
C) Good accuracy
D) Perfect prediction
Answer: A

143. Variance in ML refers to:
A) Sensitivity to training data changes
B) Hardware memory
C) CPU temperature
D) Number of files
Answer: A

144. Regularization helps to:
A) Increase overfitting
B) Reduce overfitting
C) Remove labels
D) Increase missing values
Answer: B

145. Which regularization is also called Lasso?
A) L1
B) L2
C) Dropout
D) PCA
Answer: A

146. Which regularization is also called Ridge?
A) L1
B) L2
C) L3
D) None
Answer: B

147. Clustering means:
A) Grouping similar data points
B) Predicting exact number
C) Removing rows
D) File storage
Answer: A

148. Outlier is:
A) Similar point
B) Unusual data point
C) Target variable
D) Missing column
Answer: B

149. Reinforcement learning learns by:
A) Labeled data
B) Rewards and penalties
C) Clustering only
D) PCA
Answer: B

150. Which of the following is an evaluation metric for regression?
A) Accuracy
B) Precision
C) RMSE
D) Recall
Answer: C

Data Science MCQs

151. Data Science combines:
A) Statistics
B) Programming
C) Domain knowledge
D) All of these
Answer: D

152. Which library is mainly used for data analysis in Python?
A) Pandas
B) Tkinter
C) Pygame
D) Requests
Answer: A

153. Which library is mainly used for numerical computing?
A) NumPy
B) Flask
C) Django
D) BeautifulSoup
Answer: A

154. Which library is used for plotting graphs?
A) Matplotlib
B) os
C) sys
D) math
Answer: A

155. Data cleaning means:
A) Washing computer
B) Handling missing, wrong, or duplicate data
C) Deleting all data
D) Formatting disk
Answer: B

156. Missing values can be handled by:
A) Removing rows
B) Filling values
C) Both A and B
D) None
Answer: C

157. Duplicate data should usually be:
A) Increased
B) Ignored always
C) Removed
D) Encrypted
Answer: C

158. A dataset row generally represents:
A) Feature
B) Record or observation
C) Column name
D) Error
Answer: B

159. A dataset column generally represents:
A) Feature or variable
B) Observation
C) Graph
D) File
Answer: A

160. CSV stands for:
A) Common Separated Values
B) Comma Separated Values
C) Column Stored Values
D) Computer Separated Variables
Answer: B

161. Which function reads CSV in pandas?
A) pd.open_csv()
B) pd.read_csv()
C) pd.load_csv()
D) pd.csv()
Answer: B

162. Which function shows first rows of dataframe?
A) top()
B) head()
C) first()
D) show()
Answer: B

163. Which function shows last rows of dataframe?
A) end()
B) tail()
C) last()
D) back()
Answer: B

164. Which function gives summary information of dataframe?
A) info()
B) shape()
C) tail()
D) loc()
Answer: A

165. shape returns:
A) Only rows
B) Only columns
C) Rows and columns
D) Sum of data
Answer: C

166. Which function gives statistical summary?
A) describe()
B) explain()
C) summary()
D) stats()
Answer: A

167. Mean is:
A) Middle value
B) Most frequent value
C) Average value
D) Highest value
Answer: C

168. Median is:
A) Average
B) Middle value
C) Most frequent value
D) Total value
Answer: B

169. Mode is:
A) Least common value
B) Most common value
C) Middle value
D) Difference
Answer: B

170. Standard deviation measures:
A) Central value
B) Spread of data
C) Number of columns
D) Accuracy
Answer: B

171. Variance is:
A) Square root of standard deviation
B) Square of standard deviation
C) Mean of mode
D) Median of data
Answer: B

172. Correlation measures:
A) Storage size
B) Relationship between variables
C) Number of rows
D) Type of graph
Answer: B

173. Positive correlation means:
A) One increases, other decreases
B) Both move in same direction
C) No relation
D) Random values
Answer: B

174. Negative correlation means:
A) Both increase
B) Both decrease
C) One increases, other decreases
D) No value
Answer: C

175. Which chart is used for categorical comparison?
A) Bar chart
B) Histogram
C) Scatter plot
D) Line chart
Answer: A

176. Which chart is used for frequency distribution?
A) Histogram
B) Pie chart
C) Scatter plot
D) Table
Answer: A

177. Which chart is used to show relationship between two numeric variables?
A) Scatter plot
B) Bar chart
C) Pie chart
D) Box title
Answer: A

178. Box plot is useful to detect:
A) Threads
B) Outliers
C) Folders
D) Labels
Answer: B

179. Data preprocessing includes:
A) Cleaning
B) Transformation
C) Encoding
D) All of these
Answer: D

180. Normalization is used to:
A) Scale data to common range
B) Delete data
C) Increase errors
D) Make graphs colorful
Answer: A

181. Standardization usually transforms data to:
A) Mean 0 and standard deviation 1
B) Mean 1 and std 0
C) Only positive values
D) Binary values
Answer: A

182. Categorical data can be encoded using:
A) One-hot encoding
B) Label encoding
C) Both
D) None
Answer: C

183. EDA stands for:
A) Exploratory Data Analysis
B) External Data Access
C) Effective Data Array
D) Extra Data Analysis
Answer: A

184. The purpose of EDA is:
A) Understand data
B) Find patterns
C) Detect issues
D) All of these
Answer: D

185. Which pandas function removes missing values?
A) dropna()
B) fillna()
C) remove()
D) delete()
Answer: A

186. Which pandas function fills missing values?
A) addna()
B) putna()
C) fillna()
D) replacenaa()
Answer: C

187. Which pandas function removes duplicates?
A) duplicatedrop()
B) drop_duplicates()
C) remove_duplicates()
D) unique_remove()
Answer: B

188. Big data is characterized by:
A) Volume
B) Velocity
C) Variety
D) All of these
Answer: D

189. Structured data is usually stored in:
A) Tables
B) Random photos
C) Audio only
D) Video only
Answer: A

190. Unstructured data example is:
A) Relational table
B) Database schema
C) Image file
D) Excel column name
Answer: C

191. Which SQL clause is used to filter rows?
A) SORT BY
B) FILTER
C) WHERE
D) CHECK
Answer: C

192. Which SQL command is used to retrieve data?
A) GET
B) SELECT
C) OPEN
D) READ
Answer: B

193. Which measure is affected most by outliers?
A) Median
B) Mode
C) Mean
D) Range only never
Answer: C

194. A balanced dataset means:
A) Equal or near equal class distribution
B) Equal rows and columns
C) No null values
D) Only numeric data
Answer: A

195. Sampling means:
A) Taking subset of population
B) Deleting whole data
C) Creating labels
D) Drawing graphs
Answer: A

196. Population means:
A) Small selected group
B) Entire group of interest
C) Only test data
D) Outliers only
Answer: B

197. Time series data is:
A) Data collected over time
B) Image data
C) Text only
D) Categorical only
Answer: A

198. Feature engineering means:
A) Making buildings
B) Creating useful input features
C) Deleting labels
D) Formatting system
Answer: B

199. Data visualization helps to:
A) Understand patterns easily
B) Communicate results
C) Find trends
D) All of these
Answer: D

200. The main goal of data science is:
A) Store files only
B) Extract insights from data
C) Build hardwareD) Type documents only
Answer: B
"""

with app.app_context():
    admin = User.query.filter_by(role='Admin').first()
    admin_id = admin.id if admin else 1

    sections = re.split(r'\n(perating Systems MCQs|Python MCQs|Machine Learning MCQs|Data Science MCQs)\n', text_data)
    
    current_subject = None
    for item in sections:
        if "MCQs" in item:
            subj_name = item.replace("MCQs", "").strip()
            if subj_name == "perating Systems":
                subj_name = "Operating Systems"
            
            subj = Subject.query.filter_by(name=subj_name).first()
            if not subj:
                subj = Subject(name=subj_name, created_by=admin_id)
                db.session.add(subj)
                db.session.commit()
            current_subject = subj
            
            exam = Exam.query.filter_by(title=f"{subj_name} Midterm", subject_id=subj.id).first()
            if not exam:
                exam = Exam(title=f"{subj_name} Midterm", duration=60, subject_id=subj.id, teacher_id=admin_id)
                db.session.add(exam)
                db.session.commit()
            print(f"Created Subject: {subj_name} and Exam: {exam.title}")
            
        elif item.strip():
            # parse questions
            questions = re.findall(r'(\d+)\.\s+(.*?)\nA\)\s+(.*?)\nB\)\s+(.*?)\nC\)\s+(.*?)\nD\)\s+(.*?)\nAnswer:\s+([A-D])', item, re.DOTALL)
            
            for q_match in questions:
                q_num, q_text, optA, optB, optC, optD, correct = q_match
                
                exam = Exam.query.filter_by(subject_id=current_subject.id).first()
                if exam:
                    options = {
                        "A": optA.strip(),
                        "B": optB.strip(),
                        "C": optC.strip(),
                        "D": optD.strip()
                    }
                    
                    question = Question(
                        exam_id=exam.id,
                        type="MCQ",
                        content=q_text.strip(),
                        options=json.dumps(options),
                        correct_answer=correct.strip(),
                        marks=1,
                        difficulty="Medium"
                    )
                    db.session.add(question)
                    exam.total_marks += 1
            db.session.commit()
            print(f"Parsed and added questions for {current_subject.name}")

print("Import process completed!")
