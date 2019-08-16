--
-- Name: possumjunk3; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE possumjunk3 FROM PUBLIC;
REVOKE ALL ON TABLE possumjunk3 FROM agrbrdf;
GRANT ALL ON TABLE possumjunk3 TO agrbrdf;
GRANT SELECT ON TABLE possumjunk3 TO gbs;


