#########################################################################
#
#   classifiers.py - This file is part of the Spectral Python (SPy) package.
#
#   Copyright (C) 2013 Thomas Boggs
#
#   Spectral Python is free software; you can redistribute it and/
#   or modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 2
#   of the License, or (at your option) any later version.
#
#   Spectral Python is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this software; if not, write to
#
#               Free Software Foundation, Inc.
#               59 Temple Place, Suite 330
#               Boston, MA 02111-1307
#               USA
#
#########################################################################
#
# Send comments to:
# Thomas Boggs, tboggs@users.sourceforge.net
#
'''Runs unit tests for classification routines

To run the unit tests, type the following from the system command line:

    # python -m spectral.tests.classifiers
'''

import numpy as np
import spectral as spy
from numpy.testing import assert_allclose
from spytest import SpyTest, test_method


class ClassifierTest(SpyTest):
    '''Tests various classfication functions.'''

    def setup(self):
        self.image = spy.open_image('92AV3C.lan')
        self.data = self.image.load()
        self.gt = spy.open_image('92AV3GT.GIS').read_band(0)
        self.ts = spy.create_training_classes(self.data, self.gt,
                                              calc_stats=True)

    def test_save_training_sets(self):
        '''Test that TrainingClassSet data can be saved without exception.'''
        ts = spy.create_training_classes(self.data, self.gt, calc_stats=True)
        ts.save('92AV3C.classes')

    def test_load_training_sets(self):
        '''Test that the data loaded is the same as was saved.'''
        ts = spy.create_training_classes(self.data, self.gt, calc_stats=True)
        ts.save('92AV3C.classes')
        ts2 = spy.load_training_sets('92AV3C.classes', image=self.data)
        ids = ts.classes.keys()
        for id in ids:
            s1 = ts[id]
            s2 = ts2[id]
            assert(s1.index == s2.index)
            np.testing.assert_almost_equal(s1.class_prob, s2.class_prob)
            assert_allclose(s1.stats.mean, s2.stats.mean)
            assert_allclose(s1.stats.cov, s2.stats.cov)
            np.testing.assert_equal(s1.stats.nsamples, s2.stats.nsamples)

    def test_gmlc_spectrum_image_equal(self):
        '''Tests that classification of spectrum is same as from image.'''
        gmlc = spy.GaussianClassifier(self.ts, min_samples=600)
        data = self.data[20: 30, 30: 40, :]
        assert(gmlc.classify_spectrum(data[2, 2]) == \
               gmlc.classify_image(data)[2, 2])

    def test_mahalanobis_class_mean(self):
        '''Test that a class's mean spectrum is classified as that class.
        Note this assumes that class priors are equal.
        '''
        mdc = spy.MahalanobisDistanceClassifier(self.ts)
        cl = mdc.classes[0]
        assert(mdc.classify(cl.stats.mean) == cl.index)

    def test_mahalanobis_spectrum_image_equal(self):
        '''Tests that classification of spectrum is same as from image.'''
        mdc = spy.MahalanobisDistanceClassifier(self.ts)
        data = self.data[20: 30, 30: 40, :]
        assert(mdc.classify_spectrum(data[2, 2]) == \
               mdc.classify_image(data)[2, 2])


def run():
    print '\n' + '-' * 72
    print 'Running classifier tests.'
    print '-' * 72
    test = ClassifierTest()
    test.run()

if __name__ == '__main__':
    from spectral.tests.run import parse_args, reset_stats, print_summary
    parse_args()
    reset_stats()
    run()
    print_summary()
