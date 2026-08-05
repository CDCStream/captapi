"""Linkme profile: TanStack $tsr hydration, not HTML meta/footer."""

from __future__ import annotations

from app.routers import creator_pages as cp

# Minimal dehydrated profile + featuredLinks (danucd-shaped).
_TSR = r'''
<script class="$tsr">
({initialData:$R[1]={featuredLinks:$R[2]={meta:$R[3]={totalRecords:2},list:$R[4]=[$R[5]={id:1,title:"Twitch",description:null,image:"",url:"https://twitch.tv/danucd",thumbnail:""},$R[6]={id:2,title:"YouTube",description:null,image:"",url:"https://youtube.com/@danucd",thumbnail:""}]}},profile:$R[7]={id:"abc",firstName:"Dana",lastName:"",username:"danucd",verifiedAccount:0,bio:"ALL MY LINKS",isAmbassador:1,profileVisitCount:"15.9k",isDefaultProfilePicture:!1,profileImage:"user-profile/1/a.png",profileImageWebp:"webp-images/user-profile/1/a.webp",isPrivate:0,createdAt:"2024-11-01 12:37:51",updatedAt:"2025-11-16 13:43:17",stripeStatus:$R[8]={tipsEnabled:0,stripeAccountId:"",stripeEnabled:!1},totalLinks:7,chatID:"LinkMe-1",infoLinks:$R[9]=[$R[10]={title:"Email",linkId:1,links:$R[11]=[$R[12]={linkValue:"dana.danucd@gmail.com",faceValue:"x"}]}],webLinks:$R[13]=[$R[14]={title:"Instagram",linkId:4,links:$R[15]=[$R[16]={linkValue:"https://www.instagram.com/danucd/",faceValue:"danucd"}]}]})
</script>
'''


def test_linkme_parses_tsr_not_footer() -> None:
    # Poison the HTML with the exact failure mode from production docs.
    poisoned = (
        '<html><head><title>Check out Kevin Hart (@kevinhart) on Linkme</title>'
        '<meta property="og:description" content="Discover Kevin Hart on LinkMe: Connect and see what they\'re passionate about.">'
        '<meta property="og:image" content="https://media.link.me/images/default/profile/avatar-2.png">'
        "</head><body>"
        '<a href="https://about.link.me/privacypolicy">Privacy Policy</a>'
        '<a href="https://about.link.me/termsandconditions">Terms</a>'
        + _TSR
        + "</body></html>"
    )
    out = cp._linkme_parse_page(poisoned, "https://link.me/danucd")
    assert out is not None
    assert out["username"] == "danucd"
    assert out["displayName"] == "Dana"
    assert out["bio"] == "ALL MY LINKS"
    assert out["profileVisitCount"] == "15.9k"
    assert out["totalLinks"] == 7
    assert out["isDefaultProfilePicture"] is False
    assert out["isAmbassador"] is True
    assert out["email"] == "dana.danucd@gmail.com"
    assert out["stripeStatus"]["tipsEnabled"] is False
    assert out["socials"]["instagram"] == "https://www.instagram.com/danucd/"
    assert {l["url"] for l in out["links"]} == {
        "https://twitch.tv/danucd",
        "https://youtube.com/@danucd",
    }
    assert not any("about.link.me" in (l.get("url") or "") for l in out["links"])
    assert "default/profile/avatar" not in (out.get("avatar") or "")


def test_linkme_default_avatar_flag() -> None:
    html = (
        '<script class="$tsr">({profile:$R[1]={id:"x",firstName:"Kevin",lastName:"Hart",'
        'username:"kevinhart",verifiedAccount:0,bio:"",isAmbassador:0,profileVisitCount:"29",'
        'isDefaultProfilePicture:!0,profileImage:"default/profile/avatar-2.png",isPrivate:0,'
        'createdAt:"2021-11-25 03:32:34",updatedAt:"2026-04-15 17:43:58",'
        'stripeStatus:$R[2]={tipsEnabled:0,stripeEnabled:!1},totalLinks:28,chatID:"LinkMe-1",'
        "infoLinks:null,webLinks:null},featuredLinks:$R[3]={meta:$R[4]={totalRecords:0},list:$R[5]=[]})</script>"
    )
    out = cp._linkme_parse_page(html, "https://link.me/kevinhart")
    assert out is not None
    assert out["displayName"] == "Kevin Hart"
    assert out["isDefaultProfilePicture"] is True
    assert out["totalLinks"] == 28
    assert out["links"] == []
    assert out["profileVisitCount"] == "29"


def test_linkme_credit_is_one() -> None:
    assert cp.CREDIT_PAGE["linkme"] == 1
