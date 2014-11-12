#!/usr/bin/env python
# -*- coding: UTF-8 -*-

##
## @desc: Imitate greeness's script https://gist.github.com/greeness/94a3d425009be0f94751
##        implement simple lsh and draw the result 
## @author:zhaoxm
## 

import numpy as np
import math
import matplotlib.pyplot as plt

# get number of '1's in num
# the time complexity of this way only depends on 
def bit_count(num):
    if num == 0:
        return 0
    num = num & (num - 1)
    res = 1
    while num != 0:
        res += 1
        num = num & (num - 1)
    return res

class LSH:
    dim = 2
    sig_bits = 2**10
    rand_proj = None

    def __init__(self, dim, sig_bits):
        # the data dimension
        self.dim = dim
        # random projection lines
        self.sig_bits = sig_bits
        self.rand_proj = np.random.randn(sig_bits, dim)

    def get_signature(self, user_vector):
        assert user_vector.size == self.dim
        res = 0
        for p in self.rand_proj:
            if np.dot(p, user_vector) >= 0:
                res |= 1
            res = res << 1
        return res

    # get approximate cosine of two vectors
    def approximate_cosine(self, user_vector1, user_vector2):
        a = self.get_signature(user_vector1)
        b = self.get_signature(user_vector2)
        xor = a ^ b
        xor_bitcount = bit_count(xor)
        print xor_bitcount
        return math.cos(xor_bitcount * math.pi / float(self.sig_bits))

    def cosine(self, a,b):
        dot_prod = np.dot(a,b)
        sum_a = sum(a**2) **.5
        sum_b = sum(b**2) **.5
        cosine = dot_prod/sum_a/sum_b # cosine similarity
        return cosine


def get_draw_data(dim, d, nruns):
    lsh = LSH(dim, d)
    approx_cos_list = []
    true_cos_list = []

    for run in xrange(nruns):
        user1 = np.random.randn(dim)
        user2 = np.random.randn(dim)
        true_sim, hash_sim = (lsh.cosine(user1, user2),lsh.approximate_cosine(user1, user2))
        approx_cos_list.append(hash_sim)
        true_cos_list.append(true_sim)
        diff = abs(hash_sim-true_sim)
        print 'true %.4f, hash %.4f, diff %.4f' % (true_sim, hash_sim, diff)

    return approx_cos_list, true_cos_list

if __name__ == '__main__':
    dim = 10
    d1 = 2**4
    d2 = 2**6
    d3 = 2**8
    d4 = 2**10

    nruns = 100 # repeat times
    #avg = 0

    x = np.linspace(-1, 1, 1000)
    y = x

    res1 = get_draw_data(dim, d1, nruns)
    res2 = get_draw_data(dim, d2, nruns)
    res3 = get_draw_data(dim, d3, nruns)
    res4 = get_draw_data(dim, d4, nruns)

    print 'drawing'
    fig = plt.figure()

    ax1 = fig.add_subplot(221)
    ax1.plot(x,y,color="red",linewidth=2)
    approx_cos_list, true_cos_list = res1
    t = ax1.scatter(np.array(true_cos_list), np.array(approx_cos_list))
    ax1.collections

    ax2 = fig.add_subplot(222)
    ax2.plot(x,y,color="red",linewidth=2)
    approx_cos_list, true_cos_list = res2
    t = ax2.scatter(np.array(true_cos_list), np.array(approx_cos_list))
    ax2.collections

    ax3 = fig.add_subplot(223)
    ax3.plot(x,y,color="red",linewidth=2)
    approx_cos_list, true_cos_list = res3
    t = ax3.scatter(np.array(true_cos_list), np.array(approx_cos_list))
    ax3.collections

    ax4 = fig.add_subplot(224)
    ax4.plot(x,y,color="red",linewidth=2)
    approx_cos_list, true_cos_list = res4
    t = ax4.scatter(np.array(true_cos_list), np.array(approx_cos_list))
    ax4.collections
    
    fig.show()
    fig.waitforbuttonpress()


