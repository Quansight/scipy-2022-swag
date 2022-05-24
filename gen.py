from functools import lru_cache
import yaml
from ipywidgets import interact
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import poisson_disc as pd
import matplotlib.pyplot as plt
import matplotlib.tri as tri
from matplotlib.cm import get_cmap
from scipy.stats import multivariate_normal
from matplotlib import font_manager
import numpy as np


with open("data.yml") as fi:
    data = yaml.safe_load(fi.read())

with open("groups.yaml") as fi:
    groups = yaml.safe_load(fi.read())


# try to add Raleway font
# which is the font scipy conf uses.

font_files = font_manager.findSystemFonts(fontpaths=None, fontext="ttf")
for font_file in font_files:
    if "aleway" in font_file:
        print(font_file)
    try:
        font_manager.fontManager.addfont(font_file)
    except:
        print("skip ", font_file)
        pass


## Generate multiple cards background

#### background 1

nx, ny = np.mgrid[-3:3:0.01, -4:4:0.05]
npos = np.dstack((nx, ny))

nrvs = []
centers = []
S = 13
for _ in range(int(23 * S)):
    c = (np.random.rand(2) - 0.5) * np.array([3, 4]) * 2
    centers.append(c)
    s = 0.05 + np.random.rand() * 0.1
    k = 0.3 + np.random.rand() * 0.4
    # k = 1
    if np.random.rand() > 0.5:
        k = -k
    corr = [[s / S, 0], [0, s / S]]

    rv = multivariate_normal(c, corr)
    nrvs.append((k, rv))


#### background 2
def noise(ax, cmap):
    z = np.zeros_like(nx)
    for k, rv in nrvs:
        z = z + k * rv.pdf(npos)
    ax.contourf(nx, ny, z, 15, cmap=cmap, ec="k", lw=3)
    # ax.contour(nx, ny, z, 7, colors='k', linestyles='solid')


#### background 3
sx, sy, sz, sc = np.random.rand(4, 15000) * 2 - 1


def scaback(ax, cmap):
    x, y, z, c = sx, sy, sz, sc
    x = x * 3
    y = y * 4
    z = z * 3500
    c = (c - c.min()) / (c.max() - c.min())
    ax.scatter(
        x, y, z, c, alpha=0.9, cmap=cmap, vmin=-0.5, vmax=1.5, ec="black", lw=0.5
    )


#### background 4

kx, ky = 2 * 3, 4 * 2
tripoints = pd.Bridson_sampling(np.array([kx, ky]), k=10, radius=0.2)
tric1 = np.random.rand(tripoints.shape[0], 1)


def triback(ax, cmap):
    points = tripoints
    c1 = tric1
    points = np.hstack([points, c1])

    from itertools import product

    k = []
    for dx, dy in product([-kx, 0, kx], [-ky, 0, ky]):
        k.append(points + np.array([dx, dy, 0]))

    p2 = np.vstack(k)

    x, y, c2 = p2.T
    t = tri.Triangulation(x, y)
    c2 = (c2 - c2.min()) / (c2.max() - c2.min())
    ax.tripcolor(
        t, c2, shading="flat", cmap=cmap, edgecolors="#000", vmin=-0.05, vmax=1.05
    )


####

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.cm import get_cmap

# plt.style.use('_mpl-gallery-nogrid')

# make data: correlated + noise
np.random.seed(1)
x, y, hc = np.random.rand(3, 1500)
x = x * 10 - 5
y = y * 10 - 5


# plot:


from matplotlib.patches import Circle, Wedge, Polygon
from matplotlib.collections import PatchCollection
import matplotlib.image as mpimg
from matplotlib.colors import Normalize


def plot_one(ax, cmap, name, short, desc, meth, maint, group=None, gn="0/0", tn="0/0"):
    if meth == "hex":
        ax.hexbin(
            x,
            y,
            C=hc,
            gridsize=20,
            cmap=cmap,
            vmin=-0.1,
            vmax=1,
            edgecolors="k",
            lw=0.5,
        )
    elif meth == "tri":
        triback(ax, cmap)
    elif meth == "sca":
        scaback(ax, cmap)
    elif meth == "noise":
        noise(ax, cmap)
    else:
        assert False, meth

    ax.set(xlim=(-2.72, 2.72), ylim=(-3.7, 3.7))
    ax.set_aspect("equal")
    ax.axis("off")

    def rect(top, w, bottom):
        # 4 corners
        return [[-w, bottom], [w, bottom], [w, top], [-w, top]]

    patches = [
        Polygon(rect(3, 2.1, 2.6)),  # title
        Polygon(rect(0.2, 1.9, -0.2)),  # short
        Polygon(rect(-0.4, 2.1, -2.4)),  # desc
    ]
    if not maint:
        patches.append(Polygon(rect(2.4, 2.0, 0.4)))

    axins = ax.inset_axes([-1.7, 0.4, 1.7 * 2, 2.0], transform=ax.transData)
    logo = mpimg.imread(f"logos/{name.lower()}.png")
    # newax = fig.add_axes([0.20, 0.48, 0.62, 0.22], anchor='C', zorder=1)
    if name == "stefanv":
        im = axins.imshow(logo, cmap="gray")
    else:
        im = axins.imshow(
            logo,
        )
    if maint:
        cx, cy = logo.shape[:2]
        clip = Circle((cx // 2, cy // 2), radius=cx // 2, transform=axins.transData)
        im.set_clip_path(clip)
        axins.add_patch(
            Circle(
                (cx // 2, cy // 2),
                radius=cx // 2,
                transform=axins.transData,
                fc="#ffffff00",
                ec=get_cmap(cmap)(1),
                lw=3,
            )
        )
        # patches.append(Circle((0,1.3),radius=0.77))

    axins.patch.set_alpha(0.0)
    axins.axis("off")
    # colors = [1]*len(patches)
    cc = get_cmap(cmap)(0.5)
    p = PatchCollection(patches, alpha=0.90, ec=cc, fc="white", lw=3)
    # p.set_array(colors)
    ax.add_collection(p)
    # Menlo
    # raleway
    footer = "Trade this card with other attendees. Find a pair.\nCome get more at NumFOCUS or QuanSight Booth"

    ax.text(
        0,
        2.7,
        short if maint else name,
        ha="center",
        fontsize=40,
        fontfamily="Raleway",
        fontweight="light",
        transform=ax.transData,
    )

    ax.text(
        -1.8,
        -0.1,
        group if maint else short,
        fontsize=35,
        fontfamily="Raleway",
        fontweight="light",
        transform=ax.transData,
    )
    ax.text(
        +1.8,
        -0.1,
        gn,
        ha="right",
        fontsize=35,
        fontfamily="Raleway",
        fontweight="light",
        transform=ax.transData,
    )
    ax.text(
        -2.0,
        -0.5,
        desc,
        fontsize=22,
        fontfamily="Menlo",
        fontweight="light",
        transform=ax.transData,
        va="top",
    )

    fcolor = "white" if cmap in {"gray", "twilight", "gist_heat"} else "black"
    import matplotlib.patheffects as PathEffects

    txt = ax.text(
        -2.1, -2.9, footer + " " + tn, fontsize=20, fontfamily="Raleway", color=fcolor
    )

    # txt2 = ax.text(+2.0, -2.2, tn, ha='right', fontsize=20, fontfamily='Raleway', color=fcolor)

    for t in [txt]:
        t.set_path_effects(
            [PathEffects.withStroke(linewidth=5, foreground=get_cmap(cmap)(0.5))]
        )

    # plt.show()


total = len([x for g in groups for x in g["items"]])
k = 0
for g in groups[:]:
    for i, it in enumerate(g["items"], start=1):
        k += 1
        matching = [d for d in data if d["name"].lower() == it.lower()]
        fig, ax = plt.subplots()
        fig.set_figheight(20)
        fig.set_figwidth(12)
        DPI = 150

        if len(matching) == 1:
            print(it, "- lib", k, i)
            dx = matching[0]
            plot_one(
                ax,
                cmap=g["cmap"],
                meth=g["shape"],
                name=dx["name"],
                short=g["name"],
                desc=dx["desc"],
                maint=False,
                gn=f'{i}/{len(g["items"])}',
                tn=f"{k}/{total}",
            )
        else:
            continue
            pm(ax, it, g["cmap"], g["shape"], group=g["name"])
        name = f"cards-groups/{g['name']}-{i}-{it}-card.png"
        print(name)
        fig.savefig(
            name,
            bbox_inches="tight",
            pad_inches=0,
            dpi=DPI,
        )
        plt.close("all")
