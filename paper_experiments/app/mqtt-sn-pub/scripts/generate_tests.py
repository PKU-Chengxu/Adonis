for i in range(1, 40):
    file = open('../inputs/test{}.rb'.format(i), 'r')
    data = file.read()
    data = data.replace("'mqtt-sn-pub'", "'mqtt-sn-pub-cov'")
    covfile = open('../inputs/cov-test{}.rb'.format(i), 'w')
    covfile.write(data)
    covfile.close()
    file.close()
