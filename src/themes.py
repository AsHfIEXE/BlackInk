from questionary import Style

THEMES = {
    "default": Style([
        ('question', 'fg:#673ab7 bold'),
        ('pointer', 'fg:#cc5454 bold'),
        ('highlighted', 'fg:#cc5454 bold'),
        ('selected', 'fg:#cc5454'),
        ('separator', 'fg:#cc5454'),
        ('instruction', 'fg:#cc5454'),
        ('text', 'fg:#ffffff'),
        ('answer', 'fg:#f44336 bold'),
    ]),
    "hopeful": Style([
        ('question', 'fg:#3f51b5 bold'),
        ('pointer', 'fg:#ff4081 bold'),
        ('highlighted', 'fg:#ff4081 bold'),
        ('selected', 'fg:#ff4081'),
        ('separator', 'fg:#ff4081'),
        ('instruction', 'fg:#ff4081'),
        ('text', 'fg:#ffffff'),
        ('answer', 'fg:#ff4081 bold'),
    ]),
    "melancholic": Style([
        ('question', 'fg:#212121 bold'),
        ('pointer', 'fg:#757575 bold'),
        ('highlighted', 'fg:#757575 bold'),
        ('selected', 'fg:#757575'),
        ('separator', 'fg:#757575'),
        ('instruction', 'fg:#757575'),
        ('text', 'fg:#ffffff'),
        ('answer', 'fg:#9e9e9e bold'),
    ]),
    "chaotic": Style([
        ('question', 'fg:#f44336 bold'),
        ('pointer', 'fg:#ffeb3b bold'),
        ('highlighted', 'fg:#ffeb3b bold'),
        ('selected', 'fg:#ffeb3b'),
        ('separator', 'fg:#ffeb3b'),
        ('instruction', 'fg:#ffeb3b'),
        ('text', 'fg:#ffffff'),
        ('answer', 'fg:#4caf50 bold'),
    ])
}
