from coldstation.cli import main


def test_inspect_with_sample(sample_paths, capsys):
    rc = main(["inspect", "--station", "A", "--input", str(sample_paths["A"])])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Hourly rows: 4" in out
    assert "sentinel_cells" in out


def test_inspect_missing_file(capsys):
    rc = main(["inspect", "--station", "B", "--input", "/nonexistent.xlsx"])
    assert rc == 1


def test_targets_override(sample_paths, capsys):
    rc = main(
        [
            "inspect",
            "--station",
            "C",
            "--input",
            str(sample_paths["C"]),
            "--targets",
            "ChPower01,ChPower02",
        ]
    )
    assert rc == 0
    assert "['ChPower01', 'ChPower02']" in capsys.readouterr().out
