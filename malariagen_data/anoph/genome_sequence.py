from typing import Tuple, Mapping, Sequence, Optional

import dask.array as da
import zarr  # type: ignore
from numpydoc_decorator import doc  # type: ignore

from ..util import (
    Region,
    check_types,
    da_from_zarr,
    init_zarr_store,
    parse_single_region,
)
from . import base_params
from .base import AnophelesBase


class AnophelesGenomeSequenceData(AnophelesBase):
    def __init__(
        self, virtual_contigs: Optional[Mapping[str, Sequence[str]]] = None, **kwargs
    ):
        # N.B., this class is designed to work cooperatively, and
        # so it's important that any remaining parameters are passed
        # to the superclass constructor.
        super().__init__(**kwargs)

        # Store virtual contigs.
        if virtual_contigs is None:
            virtual_contigs = dict()
        self._virtual_contigs = virtual_contigs

        # Initialize cache attributes.
        self._cache_genome = None

    @property
    def contigs(self) -> Tuple[str, ...]:
        """Contigs in the reference genome."""
        return tuple(self.config["CONTIGS"])

    @property
    def virtual_contigs(self) -> Mapping[str, Sequence[str]]:
        """Virtual contigs made by concatenating contigs in the reference genome."""
        return self._virtual_contigs

    @property
    def _genome_zarr_path(self) -> str:
        return self.config["GENOME_ZARR_PATH"]

    @property
    def _genome_fasta_path(self) -> str:
        return self.config["GENOME_FASTA_PATH"]

    @property
    def _genome_fai_path(self) -> str:
        return self.config["GENOME_FAI_PATH"]

    @property
    def _genome_ref_id(self) -> str:
        return self.config["GENOME_REF_ID"]

    @property
    def _genome_ref_name(self) -> str:
        return self.config["GENOME_REF_NAME"]

    @check_types
    @doc(
        summary="Open the reference genome zarr.",
        returns="Zarr hierarchy containing the reference genome sequence.",
    )
    def open_genome(self) -> zarr.hierarchy.Group:
        if self._cache_genome is None:
            path = f"{self._base_path}/{self._genome_zarr_path}"
            store = init_zarr_store(fs=self._fs, path=path)
            self._cache_genome = zarr.open_consolidated(store=store)
        return self._cache_genome

    def _genome_sequence_for_contig(self, *, contig, inline_array, chunks):
        """Obtain the genome sequence for a given contig as an array."""

        # Handle virtual contigs.
        if contig in self.virtual_contigs:
            # Concatenate sequences from multiple contigs in the reference genome.
            contigs = self.virtual_contigs[contig]
            seqs = [
                self._genome_sequence_for_contig(
                    contig=c, inline_array=inline_array, chunks=chunks
                )
                for c in contigs
            ]
            return da.concatenate(seqs)

        # Handle normal contigs in the reference genome.
        else:
            assert contig in self.contigs
            root = self.open_genome()
            z = root[contig]
            d = da_from_zarr(z, inline_array=inline_array, chunks=chunks)
            return d

    @check_types
    @doc(
        summary="Access the reference genome sequence.",
        returns="""
            An array of nucleotides giving the reference genome sequence for the
            given contig.
        """,
    )
    def genome_sequence(
        self,
        region: base_params.region,
        inline_array: base_params.inline_array = base_params.inline_array_default,
        chunks: base_params.chunks = base_params.native_chunks,
    ) -> da.Array:
        # Parse the region parameter into a Region object.
        resolved_region: Region = parse_single_region(self, region)
        del region

        # Obtain complete sequence for the requested contig.
        d = self._genome_sequence_for_contig(
            contig=resolved_region.contig, inline_array=inline_array, chunks=chunks
        )

        # Deal with region start and stop.
        slice_start = slice_stop = None
        if resolved_region.start:
            slice_start = resolved_region.start - 1
        if resolved_region.end:
            slice_stop = resolved_region.end
        loc_region = slice(slice_start, slice_stop)

        return d[loc_region]
