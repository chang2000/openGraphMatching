f = open("validate_filtering.txt")
# wf = open("validate_reformat_ldf.txt", "w")
# of = open("validate_reformat_nlf.txt", "w")

for line in f:
    line_item = line.split(' ')
    if line_item[0] == 'LDF,':
        ldf_string = line_item[1] 
        ldf_string = ldf_string[:-1]
        wf.write(f'{ldf_string}\n')
    elif line_item[0] == 'NLF,':
        string = line_item[1] 
        string = string[:-1]
        # of.write(f'{string}\n')

# wf.close()
# of.close()


    
