--
-- Name: harvestwheatchip_annotation; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE harvestwheatchip_annotation FROM PUBLIC;
REVOKE ALL ON TABLE harvestwheatchip_annotation FROM agrbrdf;
GRANT ALL ON TABLE harvestwheatchip_annotation TO agrbrdf;
GRANT SELECT ON TABLE harvestwheatchip_annotation TO gbs;


