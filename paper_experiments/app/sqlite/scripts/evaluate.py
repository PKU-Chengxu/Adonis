# a tiny scripts to evaluate the coverage for the batch test result
app = "sqlite"

import json
import argparse
import os
from numpy import average
import traceback

block_level = False

func_define_len = 1

total_bb = { "sqlite": -1 }

def main():
    print("evaluating coverage for application <{}>...".format(app))
    
    result = evaluate(app)
    summary(result)


def evaluate(app):
    ground_truth_dir = "../cov_trace/"
    analyse_dir = "../../../../result/" + app
    result = {} # key: test case #, value: evaluate result
    test_cases = os.listdir(analyse_dir)
    test_cases = sorted(test_cases)
    ground_truths = os.listdir(ground_truth_dir)
    for test_case in test_cases:
        # print(test_case)
        i = int(test_case.split("_")[-1])
        result["test_{:0>3d}".format(i)] = evaluate_one(app, i, ground_truth_dir, analyse_dir)
    
    of = "{}_eva_result.json".format(app)
    ofp = open(of, "w")
    print("writing evaluation results to", of)
    json.dump(result, ofp, indent=2)

    return result



def evaluate_one(app, i, gd, ad):
    # evaluate one test case
    # i is the index of the test cases
    # gd for ground truth dir
    # ad for analyse result dir
    print("evaluate test case {}".format(i))
    ground_truth_file = gd + "/trace_{:0>3d}.json".format(i)
    result_dir = ad + "/trace_{:0>3d}".format(i)
    result = {
        "ground_truth": ground_truth_file,
        "ana_result": result_dir,
        "recall": [],
        "precision": [],
        "accuracy": [],
        "max_recall_files": [],
        "max_precision_files": [],
        "max_acc_files": [],
        "uncovered_lines": []
    }
    files = os.listdir(result_dir)
    full_path_num = len([_ for _ in files if "full_path" in _]) // 2
    MPP_num = len([_ for _ in files if "MPP" in _]) // 2
    max_precision = 0
    max_recall = 0
    max_acc = 0
    for j in range(full_path_num):
        try:
            cov_file = result_dir + "/full_path_coverage_{:0>2d}.json".format(j)
            cov, uncov_lines = cal_cov(cov_file, ground_truth_file)
            if cov > max_recall:
                max_recall = cov
                result["max_recall_files"] = [cov_file]
                result["uncovered_lines"] = uncov_lines
            elif cov == max_recall:
                result["max_recall_files"].append(cov_file)
            result["recall"].append(cov)
        except Exception as e:
            raise e
        # block level accuracy
        try:
            abp_file = result_dir + "/full_path_00.json"
            mpp_file = result_dir + "/full_path_00.json"
            bb2line_file = "../../../../adonis_res/{}_bb2line.json".format(app)
            bb2line_fp = open(bb2line_file, "r")
            bb2line = json.load(bb2line_fp)
            bb2line_fp.close()
            accuracy = cal_accuracy(ground_truth_file, abp_file, mpp_file, bb2line, app)
            if accuracy > max_acc:
                max_acc = accuracy
                result["max_acc_files"] = [abp_file]
            elif accuracy == max_acc:
                result["max_acc_files"].append(abp_file)
            result["accuracy"].append(accuracy)
        except FileNotFoundError:
            continue
    for j in range(MPP_num):
        try:
            # precision
            cov_file = result_dir + "/full_path_coverage_{:0>2d}.json".format(j)
            precision, wrong_lines = cal_precision(cov_file, ground_truth_file)
            if precision > max_precision:
                max_precision = precision
                result["max_precision_files"] = [cov_file]
                result["wrong_lines"] = wrong_lines
            elif precision == max_precision:
                result["max_precision_files"].append(cov_file)
            result["precision"].append(precision)
        except Exception as e:
            raise e
            continue
    return result


def cal_cov(arf, gtf):
    # calculate the coverage given the analyzing result file (arf) and the groundtruth file (gtf)
    # print(gtf)
    arfp = open(arf, "r")
    gtfp = open(gtf, "r")
    ar = json.load(arfp)
    gt = json.load(gtfp)
    arfp.close()
    gtfp.close()
    exe_num = 0
    cov_num = 0
    uncov_lines = []
    for _ in gt:
        # print(_)
        filename = _["name"]
        exe_lines = _["executed_lines"]
        cov_lines = ar[filename.replace("-cov", "")]
        # print(filename)
        # print(exe_lines)
        for exe_line in exe_lines:
            exe_num += 1
            if covered(exe_line, cov_lines):
                cov_num += 1
            else:
                uncov_lines.append(exe_line)
    return cov_num/exe_num, uncov_lines


def cal_precision(arf, gtf):
    # calculate the coverage given the analyzing result file (arf) and the groundtruth file (gtf)
    arfp = open(arf, "r")
    gtfp = open(gtf, "r")
    ar = json.load(arfp)
    gt = json.load(gtfp)
    arfp.close()
    gtfp.close()
    ana_num = 0
    exe_num = 0
    wrong_lines = []
    for _ in gt:
        filename = _["name"]
        exe_lines = _["executed_lines"]
        cov_lines = ar[filename.replace("-cov", "")]
        for interval in cov_lines:
            if interval[1] - interval[0] < 0:
                continue
            # block-level precision
            len = interval[1] - interval[0]
            ana_num += len
            found = False
            for i in range(interval[0], interval[1] + 1):
                if i in exe_lines:
                    # for some diffrence in WASM and gcov (e.g., for varible define code, gcov will not consider it as executed), 
                    # we consider a basicblock is correct as long as part of its line is recorded by gcov
                    found = True 
                    break
            if found:
                exe_num += len
            else:
                wrong_lines.append(interval)
            # ana_num += 1
            # exe_num += executed(interval, exe_lines)
                
    return exe_num/ana_num, wrong_lines


def cal_accuracy(gtf, ambf, mppf, bb2line, app):
    # gtf - ground truth file
    # ambf - ambigurous path file
    # mppf - most possilbe path file
    # bb2line - bb2line
    global total_bb
    gtfp = open(gtf, "r")
    ambfp = open(ambf, "r")
    mppfp = open(mppf, "r")
    gt = json.load(gtfp)
    amb = json.load(ambfp)
    mpp = json.load(mppfp)
    gtfp.close()
    ambfp.close()
    mppfp.close()

    exe_info = {}
    for _ in gt:
        filename = _["name"]
        filename = filename.replace("-cov", "")
        exe_lines = _["executed_lines"]
        exe_info[filename] = exe_lines

    if total_bb[app] == -1:
        total_bb[app] = cal_total_bb(bb2line, exe_info)
        # print("total bb number:", len(total_bb[app]))
    all_bbs = total_bb[app]
    correct = 0
    # all bbs not in amb are considered not executed
    bbs_in_amb = extract_bbs_from_amb(amb)
    bbs_not_in_amb = list(set(all_bbs) - set(bbs_in_amb))
    for bb in bbs_not_in_amb:
        bb_file_name = get_file_name_from_bb2line_item(bb2line[bb])
        f, t = get_interval_from_bb2line_item(bb2line[bb])
        if bb_file_name not in exe_info:
            continue
        exe_lines_in_file = exe_info[bb_file_name]
        exe_flag = False
        for i in range(f, t+1):
            if i in exe_lines_in_file:
                exe_flag = True
                break
        if not exe_flag:
            correct += 1
    # all bbs in mpp are considered executed
    for bb in bbs_in_amb:
        bb_file_name = get_file_name_from_bb2line_item(bb2line[bb])
        f, t = get_interval_from_bb2line_item(bb2line[bb])
        if bb_file_name not in exe_info:
            continue
        exe_lines_in_file = exe_info[bb_file_name]
        exe_flag = False
        for i in range(f, t+1):
            if i in exe_lines_in_file:
                exe_flag = True
                break
        if exe_flag:
            correct += 1
    return correct/len(all_bbs)

def cal_total_bb(bb2line, exe_info):
    # return list(bb2line.keys())
    ret = []
    for k in bb2line:
        v = bb2line[k]
        file_name = get_file_name_from_bb2line_item(v)
        if file_name in exe_info:
            ret.append(k)
    return ret


def extract_bbs_from_mpp(mpp):
    ret = []
    try:
        path = mpp["path"]
        path_remove_entry_and_exit = [bb for bb in path if "block" in bb]
        ret += path_remove_entry_and_exit
        for child in mpp["children"]:
            ret += extract_bbs_from_mpp(child)
    except KeyError:
        return list(set(ret))
    return list(set(ret))


def extract_bbs_from_amb(abp):
    ret = []
    try:
        path = abp["may_bbs"]
        path_remove_entry_and_exit = [bb for bb in path if "block" in bb]
        ret += path_remove_entry_and_exit
        for child in abp["children"]:
            ret += extract_bbs_from_amb(child)
    except KeyError:
        return list(set(ret))
    return list(set(ret))

def get_file_name_from_bb2line_item(v):
    f, t = v.split("->")
    f, t = f[1:-1], t[1:-1]
    file_name = f.split(",")[0][1:-1]
    return file_name

def get_interval_from_bb2line_item(v):
    try:
        f, t = v.split("->")
        f, t = f[1:-1], t[1:-1]
        f = int(f.split(",")[1])
        t = int(t.split(",")[1])
        if f <= t:
            return f, t
        else:
            return t, f
    except ValueError:
        return 0, 0


def covered(a, intervels):
    for interval in intervels:
        # gcov will consider function define as executed but our framework will not
        # so we expand the intervel by one
        if a >= interval[0] - func_define_len and a <= interval[1] + func_define_len:
            return True
    return False


def executed(interval, exe_lines):
    res = 0
    for i in range(interval[0], interval[1] + 1):
        if i in exe_lines:
            res += 1
            break
    return res


def summary(result):
    print("recall (i.e., coverage)")
    max_cov = []
    for _ in result.values():
        if _["recall"] == []:
            continue
        max_cov.append(average(_["recall"]))
    print("avg: ", average(max_cov))
    print("min: ", min(max_cov))
    print("max: ", max(max_cov))

    print("precision")
    avg_precision = []
    for _ in result.values():
        if _["precision"] == []:
            continue
        # for system call trace, Adonis can report many (tens of) possible paths, making it unfriendly to developers
        # so for fairness, we only test the four paths that Adonis thinks have higher possiblity
        avg_precision.append(average(_["precision"][:4])) 
    print("avg: ", average(avg_precision))
    print("min: ", min(avg_precision))
    print("max: ", max(avg_precision))


    print("acc (i.e., block level accuracy)")
    mac_acc = []
    for _ in result.values():
        if _["accuracy"] == []:
            continue
        mac_acc.append(average(_["accuracy"]))
    print("avg: ", average(mac_acc))
    print("min: ", min(mac_acc))
    print("max: ", max(mac_acc))

if __name__ == "__main__":
    main()
    




