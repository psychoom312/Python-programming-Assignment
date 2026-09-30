import sys

def solve():
    input_data = sys.stdin.read().splitlines()
    if not input_data:
        return
        
    first_line = input_data[0].split()
    n = int(first_line[0])
    k = int(first_line[1])
    m = int(first_line[2])
    
    semester_students = {}
    subject_toppers = {i: [-1, []] for i in range(m)}
    
    for i in range(1, n + 1):
        if i >= len(input_data):
            break
        line = input_data[i].split()
        if not line:
            continue
            
        enrollment = line[0]
        name = line[1]
        semester = int(line[2])
        cpi = float(line[3])
        
        marks = [int(x) for x in line[4:4+m]]
        avg_marks = sum(marks) / m if m > 0 else 0.0
        
        if semester not in semester_students:
            semester_students[semester] = []
        semester_students[semester].append((enrollment, name, cpi, avg_marks))
        
        for sub_idx, mark in enumerate(marks):
            if mark > subject_toppers[sub_idx][0]:
                subject_toppers[sub_idx] = [mark, [enrollment]]
            elif mark == subject_toppers[sub_idx][0]:
                subject_toppers[sub_idx][1].append(enrollment)

    for sem in sorted(semester_students.keys()):
        students = semester_students[sem]
        students.sort(key=lambda x: (-x[2], -x[3], x[0]))
        top_k = [student[0] for student in students[:k]]
        print(f"Semester {sem}: {' '.join(top_k)}")
        
    for sub_idx in range(m):
        sub_code = f"S{sub_idx + 1}"
        topper_list = subject_toppers[sub_idx][1]
        print(f"{sub_code}: {' '.join(topper_list)}")

if __name__ == '__main__':
    solve()
