# ----------------------------------------------------------------------------
# Copyright (c) 2013--, scikit-bio development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

from __future__ import absolute_import, division, print_function
from future.utils import with_metaclass

from abc import ABCMeta

from skbio.util import classproperty, abstractproperty
from ._iupac_sequence import IUPACSequence, _motifs as parent_motifs


class NucleotideSequence(with_metaclass(ABCMeta, IUPACSequence)):
    """Base class for nucleotide sequences.

    A `NucleotideSequence` is a `Sequence` with additional methods
    that are only applicable for nucleotide sequences, and containing only
    characters used in the IUPAC DNA or RNA lexicon.

    See Also
    --------
    Sequence

    Notes
    -----
    All uppercase and lowercase IUPAC DNA/RNA characters are supported.

    .. shownumpydoc

    """
    @property
    def _motifs(self):
        return _motifs

    @abstractproperty
    @classproperty
    def complement_map(cls):
        """Return the mapping of characters to their complements.

        Returns
        -------
        dict
            Mapping of characters to their complements.

        Notes
        -----
        Complements cannot be defined for a generic `NucleotideSequence`
        because the complement of 'A' is ambiguous.
        `NucleotideSequence.complement_map` will therefore be the empty dict.
        Thanks, nature...

        .. shownumpydoc

        """
        return set()  # pragma: no cover

    def complement(self, reverse=False):
        """Return the complement of the `NucleotideSequence`

        Parameters
        ----------
        reverse : bool, optional
            If `True`, returns the reverse complement, and will reverse the
            quality scores (if they exist).

        Returns
        -------
        NucelotideSequence
            The complement of `self`. Specific type will be the same as
            ``type(self)``. The type, id, description, and quality scores of
            the result will be the same as `self`.

        See Also
        --------
        reverse_complement
        complement_map

        Example
        -------
        >>> from skbio import DNA
        >>> DNA('TTCATT', id='s', quality=range(6)).complement()
        DNA('AAGTAA', length=6, id='s', quality=[0, 1, 2, 3, 4, 5])

        >>> DNA('TTCATT', id='s', quality=range(6)).complement(reverse=True)
        DNA('AATGAA', length=6, id='s', quality=[5, 4, 3, 2, 1, 0])

        .. shownumpydoc

        """
        # TODO rewrite method for optimized performance
        complement_map = self.complement_map
        seq_iterator = reversed(self) if reverse else self
        result = [complement_map[str(base)] for base in seq_iterator]

        quality = self.quality
        if self._has_quality() and reverse:
            quality = self.quality[::-1]

        return self._to(sequence=''.join(result), quality=quality)

    def reverse_complement(self):
        """Return the reverse complement of the `NucleotideSequence`

        Returns
        -------
        NucelotideSequence
            The reverse complement of `self`. Specific type will be the same as
            ``type(self)``. The type, id, description, and quality scores of
            the result will be the same as `self`. If quality scores are
            present, they will be reversed and included in the resulting
            biological sequence.

        See Also
        --------
        complement
        complement_map
        is_reverse_complement

        Example
        -------
        >>> from skbio import DNA
        >>> DNA('TTCATT', id='s', quality=range(6)).reverse_complement()
        DNA('AATGAA', length=6, id='s', quality=[5, 4, 3, 2, 1, 0])

        .. shownumpydoc

        """
        return self.complement(reverse=True)

    def is_reverse_complement(self, other):
        """Return True if `other` is the reverse complement of `self`

        Returns
        -------
        bool
            `True` if `other` is the reverse complement of `self` and `False`
            otherwise.

        See Also
        --------
        reverse_complement

        Example
        -------
        >>> from skbio import DNA
        >>> DNA('TTCATT').is_reverse_complement('AATGAA')
        True
        >>> DNA('TTCATT').is_reverse_complement('AATGTT')
        False
        >>> DNA('ACGT').is_reverse_complement('ACGT')
        True

        .. shownumpydoc

        """
        other = self._munge_to_sequence(other, 'is_reverse_complement')

        # avoid computing the reverse complement if possible
        if len(self) != len(other):
            return False
        else:
            # we reverse complement ourselves because `other` is a `Sequence`
            # object at this point and we only care about comparing the
            # underlying sequence data
            return self.reverse_complement()._string == other._string


_motifs = parent_motifs.copy()


@_motifs("purine-run")
def _motif_purine_run(sequence, min_length, exclude):
    """Identifies purine runs"""
    return sequence.slices_from_regex("([AGR]{%d,})" % min_length,
                                      exclude=exclude)


@_motifs("pyrimidine-run")
def _motif_pyrimidine_run(sequence, min_length, exclude):
    """Identifies pyrimidine runs"""
    return sequence.slices_from_regex("([CTUY]{%d,})" % min_length,
                                      exclude=exclude)

# Leave this at the bottom
_motifs.interpolate(NucleotideSequence, "find_motifs")
