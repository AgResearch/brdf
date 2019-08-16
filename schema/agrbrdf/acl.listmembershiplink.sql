--
-- Name: listmembershiplink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE listmembershiplink FROM PUBLIC;
REVOKE ALL ON TABLE listmembershiplink FROM agrbrdf;
GRANT ALL ON TABLE listmembershiplink TO agrbrdf;
GRANT SELECT,INSERT,DELETE ON TABLE listmembershiplink TO gbs;


