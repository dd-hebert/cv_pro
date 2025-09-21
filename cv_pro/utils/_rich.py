"""
Helper classes for rendering output with ``rich``.

@author: David Hebert
"""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from rich import box
from rich.columns import Columns
from rich.console import Group, RenderableType, TextType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from cv_pro.utils.config import PRIMARY_COLOR

if TYPE_CHECKING:
    from cv_pro.segment import Segment
    from cv_pro.voltammogram import Voltammogram

COLORS = {
    'primary': PRIMARY_COLOR,
}

STYLES = {
    'main': COLORS['primary'],
    'bold': f'bold {COLORS["primary"]}',
    'highlight': f'bold bright_white on {COLORS["primary"]}',
}


def truncate_title(title: str, max_length: int = 74) -> str:
    """Truncate strings longer than ``max_length`` using elipsis."""
    half = max_length // 2
    return title if len(title) < 74 else title[: half + 1] + '...' + title[-half:]


def splash(text: str, title: str, width: int = 80, **kwargs) -> Panel:
    """A pre-formatted ``Panel`` for splashes."""
    return Panel(
        Text(text, style='bold bright_white', justify='center'),
        title=Text(title, style='table.title'),
        box=box.SIMPLE,
        border_style='bright_black',
        width=width,
        **kwargs,
    )


def table_panel(
    table: Table,
    title: str,
    subtitle: TextType | None = None,
    width: int = 80,
    **kwargs,
) -> Panel:
    """A pre-formatted ``Panel`` for displaying tables."""
    return Panel(
        table,
        title=Text(title, style=STYLES['highlight']),
        subtitle=Text(subtitle, style='table.caption') if subtitle else None,
        box=box.SIMPLE,
        width=width,
        **kwargs,
    )


def fancy_panel(
    renderable: RenderableType,
    title: str,
    subtitle: TextType | None = None,
    width: int = 80,
    **kwargs,
) -> Panel:
    """A fancy pre-formatted rich ``Panel``."""
    return Panel(
        renderable,
        title=Text(title, style=STYLES['highlight']),
        subtitle=Text.assemble(subtitle, style='table.caption') if subtitle else None,
        box=box.ROUNDED,
        width=width,
        **kwargs,
    )


def simple_panel(renderable: RenderableType, title: str, **kwargs) -> Panel:
    """A simple pre-formatted rich ``Panel``."""
    return Panel(
        renderable,
        title=Text(title, style=STYLES['highlight']),
        title_align='center',
        expand=False,
        box=box.MINIMAL,
        **kwargs,
    )


def fancy_table(*columns, width: int = 77) -> Table:
    """A fancy pre-formatted rich ``Table``."""
    return Table(*columns, width=width, box=box.HORIZONTALS, collapse_padding=True)


class ProcessingOutput:
    """
    ``rich`` renderables for :class:`~cv_pro.voltammogram.Voltammogram``.

    Attributes
    ----------
    renderables : list[RenderableType]
        A list of ``rich`` renderables.
    title : str
        The title (filename) of the processed CV file.
    """

    def __init__(self, voltammogram: Voltammogram) -> None:
        """
        Create ``rich`` renderables for :class:`~cv_pro.voltammogram.Voltammogram``.

        Parameters
        ----------
        voltammogram : :class:`~cv_pro.voltammogram.Voltammogram``
            The ``Voltammogram`` to pretty-print.
        """
        self.title = truncate_title(voltammogram.name)
        renderables = ['', self.processing_panel(voltammogram)]
        log = []

        if voltammogram.is_processed:
            renderables.extend(
                [
                    '',
                    self.ehalfs_panel(voltammogram.trimmed_segments),
                ]
            )

        if log:
            renderables.extend(log)

        self.renderables = renderables

    def __rich__(self) -> Group:
        renderables = Group(*self.renderables)
        return renderables

    def _get_subtitle(self, voltammogram) -> list[Text]:
        subtitle = [
            Text.assemble(
                'Total segments: ',
                (f'{len(voltammogram.segments)}', STYLES['bold']),
            ),
        ]

        if voltammogram.reference != 0:
            subtitle.append(
                Text.assemble(
                    'Ferrocenium: ', (f'{voltammogram.reference:+} V', STYLES['bold'])
                )
            )

        return subtitle

    def processing_panel(self, voltammogram: Voltammogram) -> Panel:
        """Create a nicely formatted rich ``Panel`` for ``voltammogram``."""
        subtitle = self._get_subtitle(voltammogram)
        bold_text = partial(Text, style=STYLES['bold'])
        if not voltammogram.is_processed:
            return simple_panel(
                Text('\n').join(subtitle),
                title=self.title,
            )

        def left_table() -> Table:
            """Shows trimming and outliers info."""
            table = Table('', '', show_header=False, box=box.SIMPLE)

            table.add_row(
                'E init. (V)', bold_text(f'{voltammogram.parameters.init_E: }')
            )
            table.add_row(
                'E final (V)', bold_text(f'{voltammogram.parameters.final_E: }')
            )
            table.add_row(
                'E high (V)', bold_text(f'{voltammogram.parameters.high_E: }')
            )
            table.add_row('E low (V)', bold_text(f'{voltammogram.parameters.low_E: }'))
            table.add_row(
                'Scan rate (V/s)',
                bold_text(f'{voltammogram.parameters.scan_rate: }'),
            )

            return table

        def right_table() -> Table:
            """Shows slicing info."""
            table = Table('', '', show_header=False, box=box.SIMPLE)

            table.add_row(
                'Init. sweep direction',
                bold_text(f'{voltammogram.parameters.init_sweep_direction[1]}'),
            )
            table.add_row(
                'Sample interval (V)',
                bold_text(f'{voltammogram.parameters.sample_interval}'),
            )
            table.add_row(
                'Sensitivity (A/V)',
                bold_text(f'{voltammogram.parameters.sensitivity:.2e}'),
            )
            table.add_row(
                'Quiet time (s)', bold_text(f'{voltammogram.parameters.quiet_time}')
            )

            return table

        return fancy_panel(
            Columns([left_table(), right_table()], expand=True, align='left'),
            title=self.title,
            subtitle=Text('\t').join(subtitle),
        )

    def ehalfs_panel(self, segments: list[Segment]) -> Panel:
        tables = []
        for segment in segments[:-1]:
            i = segment.index + 1
            table = Table(f'Segment {i} → {i + 1}', box=box.SIMPLE_HEAD)

            for e, sep in zip(segment.ehalfs, segment.peak_separations):
                table.add_row('{: .3f} ({:.3f})'.format(e, sep))

            tables.append(table)

        return fancy_panel(
            Columns(tables, align='center'), title='E1/2 and Peak Separations'
        )
