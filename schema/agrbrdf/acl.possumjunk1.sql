--
-- Name: possumjunk1; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE possumjunk1 FROM PUBLIC;
REVOKE ALL ON TABLE possumjunk1 FROM agrbrdf;
GRANT ALL ON TABLE possumjunk1 TO agrbrdf;
GRANT SELECT ON TABLE possumjunk1 TO gbs;


