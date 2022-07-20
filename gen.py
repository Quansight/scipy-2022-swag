from matplotlib import font_manager
from itertools import product
from matplotlib.cm import get_cmap
from matplotlib.collections import PatchCollection
import matplotlib.patheffects as PathEffects
from matplotlib.patches import Circle, Polygon
from scipy.stats import multivariate_normal
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import numpy as np
import poisson_disc as pd
import yaml

np.random.seed(2022)

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
znoise = np.zeros_like(nx)
for k, rv in nrvs:
    znoise = znoise + k * rv.pdf(npos)
def noise(ax, cmap):
    ax.contourf(nx, ny, znoise, 15, cmap=cmap)
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

points = tripoints
c1 = tric1
points = np.hstack([points, c1])


k = []
for dx, dy in product([-kx, 0, kx], [-ky, 0, ky]):
    k.append(points + np.array([dx, dy, 0]))

p2 = np.vstack(k)

x, y, c2 = p2.T
c2 = (c2 - c2.min()) / (c2.max() - c2.min())
TRI = tri.Triangulation(x, y)

def triback(ax, cmap):
    ax.tripcolor(
        TRI, c2, shading="flat", cmap=cmap, edgecolors="#000", vmin=-0.05, vmax=1.05
    )


####


# plt.style.use('_mpl-gallery-nogrid')

# make data: correlated + noise
# np.random.seed(1)
x, y, hc = np.random.rand(3, 2000)
x = x * 10 - 5
y = y * 10 - 5


# plot:



def plot_one(ax, cmap, name, short, desc, meth, group=None, gn="0/0", tn="0/0"):
    if meth == "hex":
        ax.hexbin(
            x,
            y,
            C=hc,
            gridsize=20,
            cmap=cmap,
            vmin=-0.0,
            vmax=1,
            edgecolors="k",
            lw=0.5,
        )
    elif meth == "tri":
        triback(ax, cmap)
    elif meth == "scatter":
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
        Polygon(rect(0.2, 2.1, -0.2)),  # short
        Polygon(rect(-0.4, 2.1, -2.4)),  # desc
        Polygon(rect(2.4, 2.1, 0.4)),  # whiteish bg
    ]

    axins = ax.inset_axes([-1.7, 0.4, 1.7 * 2, 2.0], transform=ax.transData)
    logo = mpimg.imread(f"logos/{name.lower()}.png")
    # newax = fig.add_axes([0.20, 0.48, 0.62, 0.22], anchor='C', zorder=1)
    if name == "stefanv":
        im = axins.imshow(logo, cmap="gray")
    else:
        im = axins.imshow(
            logo,
        )

    axins.patch.set_alpha(0.0)
    axins.axis("off")
    cc = get_cmap(cmap)(0.5)
    p = PatchCollection(patches, alpha=0.90, ec=cc, fc="white", lw=0)
    ax.add_collection(p)

    crect = Polygon(rect(-2.55, 2.1, -3.00))  # whiteish bg
    p2 = PatchCollection([crect], alpha=0.90, ec=cc, fc=get_cmap(cmap)(0.5), lw=0)
    ax.add_collection(p2)
    footer = "Trade this card with other attendees. Find a pair.\nCome get more at NumFOCUS or QuanSight Booth"

    ax.text(
        0,
        2.7,
        name,
        ha="center",
        fontsize=40,
        fontfamily="Raleway",
        fontweight="bold",
        transform=ax.transData,
    )

    ax.text(
        -2.0,
        -0.1,
        short + " " + gn,
        fontsize=30,
        fontfamily="Menlo",
        fontweight="light",
        transform=ax.transData,
    )
    # ax.text(
    #    +2.0,
    #    -0.1,
    #    gn,
    #    ha="right",
    #    fontsize=35,
    #    fontfamily="Menlo",
    #    fontweight="light",
    #    transform=ax.transData,
    # )
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

    txt = ax.text(
        -2.0, -2.9, footer + "   " + tn, fontsize=18, fontfamily="Raleway", color=fcolor
    )

    # for t in [txt]:
    #    t.set_path_effects(
    #        [PathEffects.withStroke(linewidth=5, foreground=get_cmap(cmap)(0.5))]
    #    )



total = len([x for g in groups for x in g["items"]])
k = 0

flatten = []

gallery = []
for g in groups[:]:
    for i, it in enumerate(g["items"], start=1):
        k += 1
        matching = [d for d in data if d["name"].lower() == it.lower()]

        if len(matching) == 1:
            dx = matching[0]
            desc = dx["desc"]

            if isinstance(desc, str):
                desc = [desc]
            for d in desc:
                flatten.append(
                    dict(
                        cmap=g["cmap"],
                        meth=g["shape"],
                        name=dx["name"],
                        short=g["name"],
                        desc=d,
                        gn=f'{i}/{len(g["items"])}',
                    )
                )
        else:
            raise ValueError("matching")

total = len(flatten)
for k, var in enumerate(flatten, start=1):
    fig, ax = plt.subplots()
    fig.set_figheight(20)
    fig.set_figwidth(12)
    DPI = 150

    plot_one(
        ax,
        **var,
        tn=f"{k}/{total}",
    )
    name = f"cards-groups/{var['short']}-{k}-{var['name']}-card.png".replace(" ", "-")
    gallery.append(f"<img src='{name}' width='30%' /> ")
    print(name)
    fig.savefig(
        name,
        bbox_inches="tight",
        pad_inches=0,
        dpi=DPI,
    )
    plt.close("all")

print("you can update the readme with")
print("".join(gallery))
