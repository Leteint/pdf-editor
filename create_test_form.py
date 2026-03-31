"""
Script : génère test_form.pdf avec tous les types de champs AcroForm.
Usage  : python create_test_form.py
"""
import pikepdf
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "test_form.pdf")


# ---------------------------------------------------------------------------
# Helpers apparence (AP streams)
# ---------------------------------------------------------------------------

def _ap_checked(pdf, w, h):
    s = pdf.make_stream(f"q 2 2 {w-4} {h-4} re f Q".encode())
    s["/BBox"] = pikepdf.Array([0, 0, w, h])
    return s


def _ap_unchecked(pdf, w, h):
    s = pdf.make_stream(f"q 0.5 w 1 1 {w-2} {h-2} re s Q".encode())
    s["/BBox"] = pikepdf.Array([0, 0, w, h])
    return s


def _radio_kid(pdf, parent_ref, option_name, x, y, w=12, h=12):
    """Un bouton radio (widget enfant d'un groupe)."""
    return pdf.make_indirect(pikepdf.Dictionary(
        Type=pikepdf.Name.Annot,
        Subtype=pikepdf.Name.Widget,
        Parent=parent_ref,
        Rect=pikepdf.Array([x, y, x + w, y + h]),
        AS=pikepdf.Name.Off,
        AP=pikepdf.Dictionary(
            N=pikepdf.Dictionary({
                f"/{option_name}": _ap_checked(pdf, w, h),
                "/Off":            _ap_unchecked(pdf, w, h),
            })
        ),
    ))


# ---------------------------------------------------------------------------

def create():
    pdf = pikepdf.new()

    font = pdf.make_indirect(pikepdf.Dictionary(
        Type=pikepdf.Name.Font,
        Subtype=pikepdf.Name.Type1,
        BaseFont=pikepdf.Name.Helvetica,
        Encoding=pikepdf.Name.WinAnsiEncoding,
    ))

    # ---- Labels de la page ------------------------------------------------
    content = (
        b"BT /F1 13 Tf  72 790 Td (Nom :)           Tj ET\n"
        b"BT /F1 13 Tf  72 730 Td (Prenom :)         Tj ET\n"
        b"BT /F1 13 Tf  72 670 Td (Dossier actif :)  Tj ET\n"
        b"BT /F1 13 Tf  72 610 Td (Genre :)           Tj ET\n"
        b"BT /F1 11 Tf 165 593 Td (Homme)             Tj ET\n"
        b"BT /F1 11 Tf 240 593 Td (Femme)             Tj ET\n"
        b"BT /F1 11 Tf 315 593 Td (Autre)             Tj ET\n"
        b"BT /F1 13 Tf  72 540 Td (Categorie :)       Tj ET\n"
    )
    stream = pdf.make_stream(content)

    # ---- Champ texte : nom ------------------------------------------------
    field_nom = pdf.make_indirect(pikepdf.Dictionary(
        Type=pikepdf.Name.Annot, Subtype=pikepdf.Name.Widget,
        FT=pikepdf.Name.Tx, T=pikepdf.String("nom"),
        Rect=pikepdf.Array([155, 758, 430, 778]),
        V=pikepdf.String(""), DA=pikepdf.String("/F1 12 Tf 0 g"),
        MK=pikepdf.Dictionary(BC=pikepdf.Array([0, 0, 0])),
    ))

    # ---- Champ texte : prenom ---------------------------------------------
    field_prenom = pdf.make_indirect(pikepdf.Dictionary(
        Type=pikepdf.Name.Annot, Subtype=pikepdf.Name.Widget,
        FT=pikepdf.Name.Tx, T=pikepdf.String("prenom"),
        Rect=pikepdf.Array([155, 698, 430, 718]),
        V=pikepdf.String(""), DA=pikepdf.String("/F1 12 Tf 0 g"),
        MK=pikepdf.Dictionary(BC=pikepdf.Array([0, 0, 0])),
    ))

    # ---- Checkbox : actif -------------------------------------------------
    field_actif = pdf.make_indirect(pikepdf.Dictionary(
        Type=pikepdf.Name.Annot, Subtype=pikepdf.Name.Widget,
        FT=pikepdf.Name.Btn, T=pikepdf.String("actif"),
        Rect=pikepdf.Array([155, 652, 171, 668]),
        V=pikepdf.Name.Off, AS=pikepdf.Name.Off,
        AP=pikepdf.Dictionary(N=pikepdf.Dictionary({
            "/Yes": _ap_checked(pdf, 16, 16),
            "/Off": _ap_unchecked(pdf, 16, 16),
        })),
    ))

    # ---- Radio : genre ----------------------------------------------------
    radio_genre = pdf.make_indirect(pikepdf.Dictionary(
        FT=pikepdf.Name.Btn,
        Ff=pikepdf.Integer(32768),   # bit 16 = Radio
        T=pikepdf.String("genre"),
        V=pikepdf.Name.Off,
    ))
    kid_homme = _radio_kid(pdf, radio_genre, "Homme", 152, 580)
    kid_femme = _radio_kid(pdf, radio_genre, "Femme", 227, 580)
    kid_autre = _radio_kid(pdf, radio_genre, "Autre", 302, 580)
    radio_genre["/Kids"] = pikepdf.Array([kid_homme, kid_femme, kid_autre])

    # ---- Combobox : categorie ---------------------------------------------
    field_categorie = pdf.make_indirect(pikepdf.Dictionary(
        Type=pikepdf.Name.Annot, Subtype=pikepdf.Name.Widget,
        FT=pikepdf.Name.Ch,
        Ff=pikepdf.Integer(131072),  # bit 18 = Combo
        T=pikepdf.String("categorie"),
        Rect=pikepdf.Array([155, 518, 430, 538]),
        Opt=pikepdf.Array([
            pikepdf.String("Particulier"),
            pikepdf.String("Professionnel"),
            pikepdf.String("Association"),
        ]),
        V=pikepdf.String(""),
        DA=pikepdf.String("/F1 12 Tf 0 g"),
        MK=pikepdf.Dictionary(BC=pikepdf.Array([0, 0, 0])),
    ))

    # ---- Page -------------------------------------------------------------
    all_widgets = [
        field_nom, field_prenom, field_actif,
        kid_homme, kid_femme, kid_autre,
        field_categorie,
    ]
    page = pdf.make_indirect(pikepdf.Dictionary(
        Type=pikepdf.Name.Page,
        MediaBox=pikepdf.Array([0, 0, 595, 842]),
        Contents=stream,
        Resources=pikepdf.Dictionary(Font=pikepdf.Dictionary({"/F1": font})),
        Annots=pikepdf.Array(all_widgets),
    ))
    pdf.pages.append(pikepdf.Page(page))

    # ---- AcroForm ---------------------------------------------------------
    pdf.Root["/AcroForm"] = pikepdf.Dictionary(
        Fields=pikepdf.Array([
            field_nom, field_prenom, field_actif,
            radio_genre, field_categorie,
        ]),
        NeedAppearances=pikepdf.Boolean(True),
        DR=pikepdf.Dictionary(Font=pikepdf.Dictionary({"/F1": font})),
    )

    pdf.save(OUTPUT)
    print(f"Créé : {OUTPUT}")


if __name__ == "__main__":
    create()
