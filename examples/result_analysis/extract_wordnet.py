f = open("wordnet_ldf.txt")
wf = open("wordnet_reformat_ldf.txt", "w")

for line in f:
    line_item = line.split(' ')
    # print(line_item)
    if line_item[0] == 'LDF,':
        ldf_string = line_item[1] 
        ldf_string = ldf_string[:-1]
        wf.write(f'{ldf_string}\n')

wf.close()


    
