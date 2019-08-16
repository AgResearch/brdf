--
-- Name: geneticoblist; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneticoblist FROM PUBLIC;
REVOKE ALL ON TABLE geneticoblist FROM agrbrdf;
GRANT ALL ON TABLE geneticoblist TO agrbrdf;
GRANT SELECT ON TABLE geneticoblist TO gbs;


