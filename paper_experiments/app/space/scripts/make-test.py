# This script generates runall.sh and runall-cov.sh

limit = 100

def main():
    all = open('runall.sh', 'w')
    all_cov = open('runall-cov.sh', 'w')
    cases = open('universe', 'r')
    count = 0
    all.writelines(['mkdir -p ../outputs\n\n'])
    all_cov.writelines(['mkdir -p ../outputs\n\n'])
    for line in cases.readlines():
        line = line.strip()
        count += 1
        all.writelines(['echo ">>>>>>>>running test {}"\n'.format(count)])
        all.writelines(['../source/space {} > ../outputs/{}\n'.format(line, count)])
        all_cov.writelines(['echo ">>>>>>>>running test {}"\n'.format(count)])
        all_cov.writelines(['../source/space-cov {} > ../outputs/{}\n'.format(line, count)])
        if count == limit:
            break

if __name__ == '__main__':
    main()



