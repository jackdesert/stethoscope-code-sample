from pyramid import testing
import ipdb
import pytest
import unittest
from stethoscope.test.base_test import BaseTest
from stethoscope.models.util import PrudentIterator


class TestPrudentIterator(BaseTest):

    def test_first_is_available(self):
        it = PrudentIterator([1,2,3,4])
        self.assertTrue(it.available)

    def test_last_is_available(self):
        it = PrudentIterator([1,2,3,4])

        it.next
        it.next
        it.next

        self.assertTrue(it.available)

    def test_after_last_is_unavailable(self):
        it = PrudentIterator([1,2,3,4])

        it.next
        it.next
        it.next
        it.next

        self.assertFalse(it.available)

    def test_peek_first(self):
        it = PrudentIterator([1,2,3,4])
        self.assertEqual(it.peek, 1)

    def test_peek_last(self):
        it = PrudentIterator([1,2,3,4])
        it.next
        it.next
        it.next
        self.assertEqual(it.peek, 4)

    def test_peek_after_last(self):
        it = PrudentIterator([1,2,3,4])
        it.next
        it.next
        it.next
        it.next
        with pytest.raises(IndexError):
            it.peek

    def test_next(self):
        it = PrudentIterator([1,2,3,4])
        peek = it.peek
        self.assertEqual(peek, it.next)

