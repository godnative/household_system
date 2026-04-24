"""Member management service."""

from sqlalchemy.orm import Session, joinedload

from app.models.household import Household, Member
from app.schemas.member import MemberCreate, MemberUpdate
from app.schemas.pagination import calculate_offset


def _value(value: object | None) -> str:
    if value in {None, '', '1752-09-14'}:
        return '无'
    return str(value)


def _photo_html(photo: str | None) -> str:
    if not photo:
        return '无照片'
    src = photo
    if src.startswith('/'):
        src = f'http://127.0.0.1:8000{src}'
    return f'<img src="{src}" alt="照片" style="width:120px;height:160px;object-fit:cover;" />'


def render_member_print_html(member: Member) -> str:
    return f"""
    <div class=\"print-member\">
      <h3>教友信息</h3>
      <table border=\"1\" cellspacing=\"0\" cellpadding=\"8\" style=\"border-collapse:collapse; width:100%;\">
        <tr>
          <td width=\"80\">姓名</td>
          <td width=\"120\">{_value(member.name)}</td>
          <td width=\"100\">性别</td>
          <td width=\"100\">{_value(member.gender)}</td>
          <td width=\"180\" rowspan=\"4\" style=\"text-align:center;\">{_photo_html(member.photo)}</td>
        </tr>
        <tr>
          <td>圣名</td>
          <td>{_value(member.baptismal_name)}</td>
          <td>出生日期</td>
          <td>{_value(member.birth_date)}</td>
        </tr>
        <tr>
          <td>文化程度</td>
          <td>{_value(member.education)}</td>
          <td>与户主关系</td>
          <td>{_value(member.relation_to_head)}</td>
        </tr>
        <tr>
          <td>从事职业</td>
          <td>{_value(member.occupation)}</td>
          <td>教籍证件编号</td>
          <td>{_value(member.church_id)}</td>
        </tr>
        <tr><td colspan=\"5\"><strong>圣洗</strong> - 施行人: {_value(member.baptism_priest)} | 代父/母: {_value(member.baptism_godparent)} | 领洗时间: {_value(member.baptism_date)} | 初领圣体: {_value(member.first_communion_date)} | 备注: {_value(member.baptism_note)}</td></tr>
        <tr><td colspan=\"5\"><strong>补礼</strong> - 神父: {_value(member.supplementary_priest)} | 地点: {_value(member.supplementary_place)} | 日期: {_value(member.supplementary_date)}</td></tr>
        <tr><td colspan=\"5\"><strong>坚振</strong> - 日期: {_value(member.confirmation_date)} | 施行人: {_value(member.confirmation_priest)} | 代父/母: {_value(member.confirmation_godparent)} | 圣名: {_value(member.confirmation_name)} | 年龄: {_value(member.confirmation_age)} | 地点: {_value(member.confirmation_place)}</td></tr>
        <tr><td colspan=\"5\"><strong>婚配</strong> - 日期: {_value(member.marriage_date)} | 主礼神父: {_value(member.marriage_priest)} | 证人: {_value(member.marriage_witness)} | 宽免事项: {_value(member.marriage_dispensation_item)} | 宽免神父: {_value(member.marriage_dispensation_priest)} | 地点: {_value(member.marriage_place)}</td></tr>
        <tr><td colspan=\"5\"><strong>病人傅油</strong> - 日期: {_value(member.anointing_date)} | 施行人: {_value(member.anointing_priest)} | 地点: {_value(member.anointing_place)} | 死亡日期: {_value(member.death_date)} | 死亡年龄: {_value(member.death_age)}</td></tr>
        <tr><td colspan=\"5\"><strong>其他</strong> - 所属善会: {_value(member.association)} | 备注: {_value(member.note)}</td></tr>
      </table>
    </div>
    """


def get_member_or_404(db: Session, member_id: int) -> Member:
    """Get member by ID or raise 404."""
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='成员不存在')
    return member


def list_members(
    db: Session,
    household_id: int | None = None,
    user_village_ids: list[int] | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict], int]:
    """List members with optional filters.

    Returns tuple of (items, total_count).
    """
    query = db.query(Member).options(joinedload(Member.household).joinedload(Household.village))

    if household_id:
        query = query.filter(Member.household_id == household_id)
    elif user_village_ids is not None:
        query = query.join(Household).filter(Household.village_id.in_(user_village_ids))

    if search:
        query = query.filter(
            (Member.name.contains(search)) | (Member.baptismal_name.contains(search))
        )

    total = query.count()
    offset = calculate_offset(page, page_size)
    members = query.order_by(Member.id.desc()).offset(offset).limit(page_size).all()

    return [
        {
            'id': m.id,
            'household_id': m.household_id,
            'name': m.name,
            'gender': m.gender,
            'birth_date': m.birth_date,
            'baptismal_name': m.baptismal_name,
            'relation_to_head': m.relation_to_head,
            'photo': m.photo,
            'created_at': m.created_at,
        }
        for m in members
    ], total


def get_member_detail(db: Session, member_id: int) -> Member:
    """Get member detail."""
    member = (
        db.query(Member)
        .options(joinedload(Member.household).joinedload(Household.village))
        .filter(Member.id == member_id)
        .first()
    )
    if not member:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='成员不存在')
    return member


def create_member(db: Session, data: MemberCreate) -> Member:
    """Create a new member."""
    household = db.query(Household).filter(Household.id == data.household_id).first()
    if not household:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='家庭不存在')

    member = Member(**data.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def update_member(db: Session, member: Member, data: MemberUpdate) -> Member:
    """Update a member."""
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(member, key, value)

    db.commit()
    db.refresh(member)
    return member


def delete_member(db: Session, member: Member) -> None:
    """Delete a member."""
    db.delete(member)
    db.commit()


def set_as_household_head(db: Session, member: Member) -> Member:
    """Set member as head of household."""
    household = member.household
    household.head_of_household = member.name
    member.relation_to_head = '户主'
    db.commit()
    db.refresh(member)
    return member
